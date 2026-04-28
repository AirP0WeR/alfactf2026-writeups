import { Renderer } from './render/Renderer.js';
import { InputManager } from './input/InputManager.js';
import { ClientPlayer } from './game/ClientPlayer.js';
import { ClientBall } from './game/ClientBall.js';
import { Interpolation } from './network/Interpolation.js';
import {
  COURT_WIDTH, COURT_LENGTH, NET_Y, SHOT_REACH,
  SHOT_PARAMS, SWING_TOTAL, SWING_WINDUP, SWING_SWEET_SPOT, SWING_FOLLOW_THROUGH,
  PLAYER_STATES, GAME_STATES, PLAYER_MAX_SPEED,
  CENTER_SERVICE_X, SERVICE_LINE_DIST
} from '../../shared/constants.js';
import { STARTING_POSITIONS } from '../../shared/CourtLayout.js';
import { resolveShot } from '../../shared/ShotPhysics.js';

export class Game {
  constructor(canvas) {
    this.renderer = new Renderer(canvas);
    this.input = new InputManager();
    this.players = [];
    this.ball = new ClientBall();
    this.localPlayerId = null;
    this.score = null;
    this.message = null;
    this.messageTimer = 0;
    this.lastTime = 0;
    this.running = false;
    this.physicsAccumulator = 0;
    this.connection = null;
    this.mode = 'local';
    this.interpolation = new Interpolation();
    this.inputSeq = 0;
    this.pendingInputs = [];
    this.lastShotTime = 0;

    this.serveState = 'none';
    this.serveSide = 'deuce';
    this.servingTeam = 0;
    this.serveTossTimer = 0;
    this.serveWaitTimer = 0;
    this.serveFaults = 0;
    this.pointPauseTimer = 0;
    this.serveTiming = null;
    this.serveTimingTimer = 0;

    this.rallyTime = 0;
  }

  startLocal() {
    this.mode = 'local';

    const p1 = new ClientPlayer('local', 0, STARTING_POSITIONS.team1[0].x, STARTING_POSITIONS.team1[0].y, '');
    this.players = [p1];
    this.localPlayerId = 'local';

    const p2 = new ClientPlayer('bot1', 1, STARTING_POSITIONS.team2[0].x, STARTING_POSITIONS.team2[0].y, 'Бот');
    this.players.push(p2);

    this.score = {
      points: [0, 0],
      games: [0, 0],
      sets: [],
      servingTeam: 0,
      advantage: null
    };

    this.servingTeam = 0;
    this.serveSide = 'deuce';
    this.serveFaults = 0;

    this.showMessage('WASD — движение, Пробел — подача', 2);
    this.setupServe();
    this.serveWaitTimer = 0;

    this.running = true;
    this.lastTime = performance.now();
    this.loop();
  }

  setupServe() {
    const server = this.getServingPlayer();
    if (!server) return;

    if (this.servingTeam === 0) {
      server.x = this.serveSide === 'deuce' ? COURT_WIDTH * 0.75 : COURT_WIDTH * 0.25;
      server.y = 150;
    } else {
      server.x = this.serveSide === 'deuce' ? COURT_WIDTH * 0.25 : COURT_WIDTH * 0.75;
      server.y = COURT_LENGTH - 150;
    }
    server.vx = 0;
    server.vy = 0;

    this.ball.x = server.x;
    this.ball.y = server.y;
    this.ball.z = 80;
    this.ball.vx = 0;
    this.ball.vy = 0;
    this.ball.vz = 0;
    this.ball.spinX = 0;
    this.ball.spinY = 0;
    this.ball.bounceCount = 0;
    this.ball.state = 'serving';
    this.ball.lastHitBy = null;
    this.ball.lastSide = null;
    
    this.ball.hitTeam = null;
    this.ball.needsCross = false;

    this.serveState = 'waiting';
    this.serveTossTimer = 0;
    this.serveWaitTimer = 0;
  }

  updateServe(dt) {
    const server = this.getServingPlayer();
    if (!server) return;

    if (this.serveTimingTimer > 0) this.serveTimingTimer -= dt;

    if (this.serveState === 'waiting') {
      
      this.ball.x = server.x + (server.team === 0 ? 15 : -15);
      this.ball.y = server.y;
      this.ball.z = 70;

      if (this.input.shotJustPressed() && this.isLocalServing()) {
        this.serveState = 'tossed';
        this.serveTossTimer = 0;
        
        this.ball.vz = 500;
        this.ball.vx = 0;
        this.ball.vy = 0;
        this.ball.state = 'serving';
      }

      if (server.id === 'bot1') {
        this.serveWaitTimer += dt;
        if (this.serveWaitTimer > 1.5) {
          this.serveState = 'tossed';
          this.serveTossTimer = 0;
          this.ball.vz = 350;
          this.serveWaitTimer = 0;
        }
      }
    }

    if (this.serveState === 'tossed') {
      this.serveTossTimer += dt;

      this.ball.x = server.x + (server.team === 0 ? 15 : -15);

      const driftDir = server.team === 0 ? 1 : -1;
      this.ball.y = server.y + driftDir * this.serveTossTimer * 30;
      this.ball.vz -= 980 * dt;
      this.ball.z += this.ball.vz * dt;

      const canHit = this.serveTossTimer > 0.12 && this.ball.z > 20;

      if (this.input.shotJustPressed() && this.isLocalServing() && canHit) {
        const peakProximity = Math.abs(this.ball.vz);
        if (peakProximity < 40) this.serveTiming = 'perfect';
        else if (peakProximity < 120) this.serveTiming = 'good';
        else if (this.ball.vz > 0) this.serveTiming = 'early';
        else this.serveTiming = 'weak';
        this.serveTimingTimer = 1.0;
        this.executeServe(server);
      }

      if (server.id === 'bot1' && this.serveTossTimer >= 0.6) {
        this.serveTiming = 'perfect';
        this.serveTimingTimer = 0.5;
        this.executeServe(server);
      }

      if (this.ball.z <= 0 && this.serveTossTimer > 0.2) {
        this.ball.z = 0;
        this.ball.vz = 0;
        this.handleServeFault();
      }
    }
  }

  executeServe(server) {
    const dir = this.servingTeam === 0 ? 1 : -1;

    const peakProximity = Math.abs(this.ball.vz);
    let powerMult = 0.7, accuracySpread = 120;
    if (peakProximity < 40) { powerMult = 1.0; accuracySpread = 40; }
    else if (peakProximity < 120) { powerMult = 0.85; accuracySpread = 70; }
    else if (this.ball.vz > 0) { powerMult = 0.65; accuracySpread = 130; }
    else { powerMult = 0.6; accuracySpread = 150; }

    let boxMinX, boxMaxX, boxMinY, boxMaxY;
    if (this.servingTeam === 0) {
      boxMinY = NET_Y;
      boxMaxY = NET_Y + SERVICE_LINE_DIST;
      if (this.serveSide === 'deuce') {
        boxMinX = 0; boxMaxX = CENTER_SERVICE_X;
      } else {
        boxMinX = CENTER_SERVICE_X; boxMaxX = COURT_WIDTH;
      }
    } else {
      boxMinY = NET_Y - SERVICE_LINE_DIST;
      boxMaxY = NET_Y;
      if (this.serveSide === 'deuce') {
        boxMinX = CENTER_SERVICE_X; boxMaxX = COURT_WIDTH;
      } else {
        boxMinX = 0; boxMaxX = CENTER_SERVICE_X;
      }
    }

    const aimAngle = server.aimAngle != null ? server.aimAngle : (this.servingTeam === 0 ? Math.PI / 2 : -Math.PI / 2);
    const aimDx = Math.cos(aimAngle);
    const aimDy = Math.sin(aimAngle);

    const boxCenterX = (boxMinX + boxMaxX) / 2;
    const boxCenterY = (boxMinY + boxMaxY) / 2;
    const boxHalfW = (boxMaxX - boxMinX) / 2;
    const boxHalfH = (boxMaxY - boxMinY) / 2;

    let targetX = boxCenterX + aimDx * boxHalfW * 0.7;
    let targetY = boxCenterY + aimDy * boxHalfH * 0.5;

    const margin = 30;
    targetX = Math.max(boxMinX + margin, Math.min(boxMaxX - margin, targetX));
    targetY = Math.max(boxMinY + margin, Math.min(boxMaxY - margin, targetY));

    targetX += (Math.random() - 0.5) * accuracySpread;
    targetY += (Math.random() - 0.5) * accuracySpread * 0.4;
    targetX = Math.max(boxMinX + 10, Math.min(boxMaxX - 10, targetX));
    targetY = Math.max(boxMinY + 10, Math.min(boxMaxY - 10, targetY));

    const dx = targetX - this.ball.x;
    const dy = targetY - this.ball.y;
    const dist = Math.sqrt(dx * dx + dy * dy);

    const baseServeSpeed = 3000 + Math.random() * 800;
    const serveSpeed = baseServeSpeed * powerMult;

    this.ball.vx = (dx / dist) * serveSpeed * 0.3;
    this.ball.vy = (dy / dist) * serveSpeed;

    const g = 980;
    const netClearance = 170;
    const distToNet = Math.abs(NET_Y - this.ball.y);
    const tToTarget = Math.max(0.1, dist / serveSpeed);
    const tToNet = Math.max(0.05, distToNet / serveSpeed);
    const ballisticVz = (0.5 * g * tToTarget * tToTarget - this.ball.z) / tToTarget;
    const netVz = (netClearance - this.ball.z + 0.5 * g * tToNet * tToNet) / tToNet;
    this.ball.vz = Math.max(ballisticVz, netVz);
    this.ball.spinX = dir * (0.15 + powerMult * 0.15);
    this.ball.spinY = 0;
    this.ball.bounceCount = 0;
    this.ball.state = 'in_play';
    this.ball.lastHitBy = server.id;
    this.ball.lastSide = null;
    this.ball.isServe = true;
    this.ball.serveValidated = false;
    
    this.ball.hitTeam = null;
    this.ball.needsCross = false;

    this.serveState = 'playing';
    server.state = PLAYER_STATES.SWINGING;
    server.swingTimer = SWING_TOTAL;
    server.facing = Math.atan2(dy, dx);
  }

  handleServeFault() {
    this.serveFaults++;
    if (this.serveFaults >= 2) {
      
      this.showMessage('Двойной фол!', 1.5);
      const scoringTeam = this.servingTeam === 0 ? 1 : 0;
      this.scorePoint(scoringTeam);
    } else {
      this.showMessage('Фол!', 1.5);
      this.setupServe();
    }
  }

  isLocalServing() {
    const server = this.getServingPlayer();
    return server && server.id === this.localPlayerId;
  }

  getServingPlayer() {
    return this.players.find(p =>
      (this.servingTeam === 0 && p.team === 0) ||
      (this.servingTeam === 1 && p.team === 1)
    );
  }

  startOnline(connection) {
    this.mode = 'online';
    this.connection = connection;
    this.localPlayerId = connection.playerId;
    this.running = true;
    this.lastTime = performance.now();
    this.loop();
  }

  handleRoomState(msg) {
    if (msg.players) {
      for (const pd of msg.players) {
        if (!this.players.find(p => p.id === pd.id)) {
          const pos = pd.team === 0 ? STARTING_POSITIONS.team1[0] : STARTING_POSITIONS.team2[0];
          this.players.push(new ClientPlayer(pd.id, pd.team, pos.x, pos.y, pd.name));
        }
      }
      this.players = this.players.filter(p => msg.players.some(pd => pd.id === p.id));
    }
  }

  handleMatchStart(msg) {
    
    if (msg.players) {
      this.players = [];
      for (const pd of msg.players) {
        const p = new ClientPlayer(pd.id, pd.team, pd.x, pd.y, pd.name);
        this.players.push(p);
      }
    }
    this.showMessage('Матч начался!', 2);
  }

  handleSnapshot(snapshot) {
    this.interpolation.pushSnapshot(snapshot);

    if (snapshot.score) this.score = snapshot.score;

    if (snapshot.servePhase != null) {
      if (snapshot.servePhase === 'waiting') this.serveState = 'waiting';
      else if (snapshot.servePhase === 'tossed') this.serveState = 'tossed';
    }
    if (snapshot.state === 'playing') this.serveState = 'playing';
    if (snapshot.servingTeam != null) this.servingTeam = snapshot.servingTeam;
    if (snapshot.serveSide) this.serveSide = snapshot.serveSide;
    if (snapshot.serveFaults != null) this.serveFaults = snapshot.serveFaults;

    if (snapshot.ball) this.ball.applyServerState(snapshot.ball);

    if (snapshot.players) {
      for (const sp of snapshot.players) {
        let existing = this.players.find(p => p.id === sp.id);

        if (!existing) {
          
          existing = new ClientPlayer(sp.id, sp.team, sp.x, sp.y, sp.name);
          this.players.push(existing);
        }

        if (sp.id === this.localPlayerId) {
          const dx = sp.x - existing.x;
          const dy = sp.y - existing.y;
          if (Math.sqrt(dx * dx + dy * dy) > 500) {
            existing.applyServerState(sp);
          }
        } else {
          existing.applyServerState(sp);
        }
      }
    }
  }

  handlePointScored(msg) {
    const reasons = {
      out: 'аут',
      double_bounce: 'двойной отскок',
      no_cross: 'не перелетел сетку',
      ball_stopped: 'мяч остановился',
    };
    const reason = reasons[msg.reason] || msg.reason;
    this.showMessage(`Очко — Команда ${msg.team + 1}! (${reason})`, 2);
  }

  handleMatchEnd(msg) {
    const reason = msg.reason === 'forfeit' ? ' (Сдача)' : '';
    this.showMessage(`Матч окончен! Победила Команда ${msg.winner + 1}!${reason}`, 10);
  }

  loop() {
    if (!this.running) return;

    const now = performance.now();
    const dt = Math.min((now - this.lastTime) / 1000, 0.05);
    this.lastTime = now;

    this.update(dt);
    this.render();

    requestAnimationFrame(() => this.loop());
  }

  update(dt) {
    if (this.messageTimer > 0) {
      this.messageTimer -= dt;
      if (this.messageTimer <= 0) this.message = null;
    }

    if (this.mode === 'local') {
      const fixedDt = 1 / 60;
      this.physicsAccumulator += dt;
      while (this.physicsAccumulator >= fixedDt) {
        this.updateLocal(fixedDt);
        this.physicsAccumulator -= fixedDt;
      }
    } else {
      this.updateOnline(dt);
    }
  }

  updateLocal(dt) {
    
    if (this.pointPauseTimer > 0) {
      this.pointPauseTimer -= dt;
      if (this.pointPauseTimer <= 0) {
        this.setupServe();
      }
      return;
    }

    const localPlayer = this.getLocalPlayer();

    if (this.serveState === 'waiting' || this.serveState === 'tossed') {
      this.rallyTime = 0;
      
      if (localPlayer) {
        if (!this.isLocalServing()) {
          localPlayer.update(dt, this.input);
        } else {
          
          localPlayer.update(dt, this.input);
        }
      }
      this.updateBot(dt);
      this.updateServe(dt);
      return;
    }

    if (this.ball.state === 'in_play' && !this.ball.isServe) {
      this.rallyTime += dt;
    }

    if (localPlayer) {
      localPlayer.update(dt, this.input);

      if (this.input.shotJustPressed() && localPlayer.swingTimer <= 0) {
        this.tryShot(localPlayer);
      }

      if (localPlayer.swingTimer > 0) {
        localPlayer.swingTimer -= dt * 1000;
        if (localPlayer.swingTimer <= 0) {
          localPlayer.state = 'idle';
          localPlayer.swingTimer = 0;
        }
      }
    }

    this.updateBot(dt);
    this.ball.update(dt);

    if (this.ball.isServe && !this.ball.serveValidated && this.ball.bounceCount === 1) {
      this.ball.serveValidated = true;
      if (!this.isInServiceBox(this.ball.x, this.ball.y)) {
        this.ball.state = 'dead';
        this.handleServeFault();
        return;
      }
      this.ball.isServe = false;
    }

    if (this.ball.state === 'in_play' && this.ball.needsCross &&
        this.ball.bounceCount >= 1 && this.ball.hitTeam != null &&
        this.ball.lastSide === this.ball.hitTeam && !this.ball.isServe) {
      const scoringTeam = this.ball.hitTeam === 0 ? 1 : 0;
      this.scorePoint(scoringTeam);
      return;
    }

    if (this.ball.bounceCount >= 2 && this.ball.state === 'in_play') {
      const scoringTeam = this.ball.lastSide === 0 ? 1 : 0;
      this.scorePoint(scoringTeam);
    }

    if (this.ball.state === 'dead' && this.serveState === 'playing') {
      const lastHitter = this.players.find(p => p.id === this.ball.lastHitBy);
      if (lastHitter) {
        const scoringTeam = lastHitter.team === 0 ? 1 : 0;
        this.scorePoint(scoringTeam);
      }
    }

    if (this.ball.state === 'in_play' && this.ball.z <= 0 &&
        Math.abs(this.ball.vz) < 5 && Math.abs(this.ball.vx) < 20 && Math.abs(this.ball.vy) < 20 &&
        this.ball.bounceCount >= 1) {
      const scoringTeam = this.ball.y < NET_Y ? 1 : 0;
      this.scorePoint(scoringTeam);
    }
  }

  isInServiceBox(x, y) {
    
    if (this.servingTeam === 0) {
      
      if (y < NET_Y || y > NET_Y + SERVICE_LINE_DIST) return false;
      if (this.serveSide === 'deuce') {
        return x < CENTER_SERVICE_X;
      } else {
        return x >= CENTER_SERVICE_X;
      }
    } else {
      if (y > NET_Y || y < NET_Y - SERVICE_LINE_DIST) return false;
      if (this.serveSide === 'deuce') {
        return x >= CENTER_SERVICE_X;
      } else {
        return x < CENTER_SERVICE_X;
      }
    }
  }

  updateOnline(dt) {
    if (this.messageTimer > 0) {
      this.messageTimer -= dt;
      if (this.messageTimer <= 0) this.message = null;
    }

    if (this.serveTimingTimer > 0) this.serveTimingTimer -= dt;

    const localPlayer = this.getLocalPlayer();
    if (!localPlayer || !this.connection?.connected) return;

    localPlayer.update(dt, this.input);

    const inputData = this.input.getInput();
    inputData.seq = this.inputSeq++;
    this.connection.sendInput(inputData);

    if (this.ball.state === 'serving') {
      if (this.input.shotJustPressed()) {
        if (this.serveState === 'waiting' || this.ball.vz === 0) {
          
          this.connection.sendServeToss();
          this.serveState = 'tossed';
          this.serveTossTimer = 0;
        } else if (this.serveState === 'tossed' && this.serveTossTimer > 0.12) {
          
          this.connection.sendServeHit(localPlayer.aimAngle);
          this.serveState = 'none';
        }
      }
      
      if (this.serveState === 'tossed') {
        this.serveTossTimer += dt;
      }
    } else {

      if (this.serveState === 'tossed') this.serveState = 'none';

      // Client-side ball physics prediction
      this.ball.update(dt);

      // Swing timer for local player
      if (localPlayer.swingTimer > 0) {
        localPlayer.swingTimer -= dt * 1000;
        if (localPlayer.swingTimer <= 0) {
          localPlayer.swingTimer = 0;
          localPlayer.state = 'idle';
        }
      }

      const now = performance.now();
      if (inputData.shot && now - this.lastShotTime > 500) {
        const localP = this.getLocalPlayer();
        const aimAngle = localP ? localP.aimAngle : null;
        this.connection.sendShot(inputData.shotModifier || 'flat', aimAngle);
        this.lastShotTime = now;

        // Client-side prediction: also resolve shot locally
        if (localP && localP.swingTimer <= 0) {
          this.tryShot(localP);
        }
      }
    }
  }

  _initBotAI(bot) {
    if (bot._botAI) return;
    bot._botAI = {
      zoneSide: bot.x < COURT_WIDTH / 2 ? -1 : 1,
      homeX: bot.x < COURT_WIDTH / 2 ? COURT_WIDTH * 0.28 : COURT_WIDTH * 0.72,
      homeY: bot.team === 0 ? COURT_LENGTH * 0.2 : COURT_LENGTH * 0.8,
      aggression: 0.4 + Math.random() * 0.5,
      reactionJitter: Math.random() * 0.15,
    };
  }

  _botPickShot(bot, ball) {
    const ai = bot._botAI;
    const opponentBaseline = bot.team === 0 ? COURT_LENGTH - 200 : 200;
    const opponentMid = bot.team === 0 ? COURT_LENGTH * 0.75 : COURT_LENGTH * 0.25;

    const leftCorner  = { x: COURT_WIDTH * 0.1, y: opponentMid };
    const rightCorner = { x: COURT_WIDTH * 0.9, y: opponentMid };
    const deepMiddle  = { x: COURT_WIDTH * 0.5, y: opponentBaseline };
    const dropShort   = {
      x: bot.x + (Math.random() - 0.5) * 200,
      y: bot.team === 0 ? NET_Y + 120 : NET_Y - 120,
    };

    let shotType = 'flat';
    let target;

    if (ball.z > 180) {
      shotType = 'smash';
      target = ai.zoneSide < 0 ? leftCorner : rightCorner;
    } else {
      const roll = Math.random();
      if (roll < 0.18) {
        shotType = 'lob';
        target = deepMiddle;
      } else if (roll < 0.38 * ai.aggression) {
        shotType = 'angled';
        target = ai.zoneSide < 0 ? leftCorner : rightCorner;
        target = { x: target.x, y: bot.team === 0 ? NET_Y + 180 : NET_Y - 180 };
      } else if (roll < 0.7) {
        shotType = Math.random() < 0.35 ? 'angled' : 'flat';
        target = ai.zoneSide < 0 ? rightCorner : leftCorner;
      } else if (roll < 0.9) {
        shotType = 'flat';
        target = ai.zoneSide < 0 ? leftCorner : rightCorner;
      } else {
        shotType = 'flat';
        target = dropShort;
      }
    }

    const jitterX = (Math.random() - 0.5) * 80;
    const jitterY = (Math.random() - 0.5) * 60;
    const aimAngle = Math.atan2(
      (target.y + jitterY) - ball.y,
      (target.x + jitterX) - ball.x,
    );

    return { shotType, aimAngle };
  }

  _botMoveToward(bot, target, dt) {
    const dx = target.x - bot.x;
    const dy = target.y - bot.y;
    const dist = Math.hypot(dx, dy);

    if (dist > 15) {
      bot.vx = (dx / dist) * PLAYER_MAX_SPEED;
      bot.vy = (dy / dist) * PLAYER_MAX_SPEED;
      bot.x += bot.vx * dt;
      bot.y += bot.vy * dt;
      bot.facing = Math.atan2(dy, dx);
      if (bot.state !== PLAYER_STATES.SWINGING) bot.state = PLAYER_STATES.MOVING;
    } else {
      bot.vx = 0;
      bot.vy = 0;
      if (bot.state !== PLAYER_STATES.SWINGING) bot.state = PLAYER_STATES.IDLE;
    }

    bot.x = Math.max(20, Math.min(COURT_WIDTH - 20, bot.x));
    if (bot.team === 1) {
      bot.y = Math.max(NET_Y + 20, Math.min(COURT_LENGTH - 20, bot.y));
    } else {
      bot.y = Math.max(20, Math.min(NET_Y - 20, bot.y));
    }
  }

  updateBot(dt) {
    const bot = this.players.find(p => p.id === 'bot1');
    if (!bot) return;
    this._initBotAI(bot);
    const ai = bot._botAI;

    if (bot.swingTimer > 0) {
      bot.swingTimer -= dt * 1000;
      if (bot.swingTimer <= 0) {
        bot.swingTimer = 0;
        if (bot.state === PLAYER_STATES.SWINGING) bot.state = PLAYER_STATES.IDLE;
      }
    }

    if (this.serveState === 'waiting' && this.servingTeam === 1) return;
    if (this.ball.state === 'dead') {
      this._botMoveToward(bot, { x: ai.homeX, y: ai.homeY }, dt);
      return;
    }

    if (this.ball.state !== 'in_play') return;

    const ballHeadingToBot = (bot.team === 1 && this.ball.vy > 0) ||
                              (bot.team === 0 && this.ball.vy < 0);

    let targetX, targetY;
    if (ballHeadingToBot) {
      let leadT = 0.3;
      if (Math.abs(this.ball.vy) > 50) {
        const t = (bot.y - this.ball.y) / this.ball.vy;
        if (t > 0.05 && t < 1.5) leadT = t;
      }
      targetX = this.ball.x + this.ball.vx * leadT;
      targetY = this.ball.y + this.ball.vy * leadT;
    } else {
      // Ball heading away — retreat toward home
      targetX = ai.homeX * 0.6 + this.ball.x * 0.4;
      targetY = ai.homeY;
    }

    if (bot.team === 1) {
      targetY = Math.max(NET_Y + 150, Math.min(COURT_LENGTH - 30, targetY));
    } else {
      targetY = Math.max(30, Math.min(NET_Y - 150, targetY));
    }
    targetX = Math.max(30, Math.min(COURT_WIDTH - 30, targetX));

    this._botMoveToward(bot, { x: targetX, y: targetY }, dt);

    const botHitReach = SHOT_REACH * 0.55;
    const botBlockedByOwnHit = this.ball.hitTeam === bot.team;
    if (bot.swingTimer <= 0 && !botBlockedByOwnHit) {
      const ballDist = Math.hypot(bot.x - this.ball.x, bot.y - this.ball.y);
      if (ballDist < botHitReach && this.ball.z < 300) {
        const { shotType, aimAngle } = this._botPickShot(bot, this.ball);
        bot.aimAngle = aimAngle;
        this.executeShot(bot, shotType);
      }
    }
  }

  swingPowerMult(elapsedMs) {
    if (elapsedMs <= 0) return 0.5;
    if (elapsedMs < SWING_WINDUP) {
      return 0.5 + (elapsedMs / SWING_WINDUP) * 0.5;
    }
    if (elapsedMs < SWING_WINDUP + SWING_SWEET_SPOT) {
      return 1.0;
    }
    const fe = elapsedMs - SWING_WINDUP - SWING_SWEET_SPOT;
    return Math.max(0.5, 1.0 - (fe / SWING_FOLLOW_THROUGH) * 0.5);
  }

  tryShot(player, powerMult = 1.0) {
    if (this.ball.state !== 'in_play') return;

    if (this.ball.hitTeam === player.team) return;

    const dx = this.ball.x - player.x;
    const dy = this.ball.y - player.y;
    const dist = Math.sqrt(dx * dx + dy * dy);

    if (dist <= SHOT_REACH) {
      const inputData = this.input.getInput();
      const shotType = inputData.shotModifier || 'flat';
      this.executeShot(player, shotType, powerMult);
    }
  }

  executeShot(player, shotType, powerMult = 1.0, enterSwingState = true) {
    if (enterSwingState && player.swingTimer > 0) return;

    if (enterSwingState) {
      player.state = PLAYER_STATES.SWINGING;
      player.swingTimer = SWING_TOTAL;
    }

    const aimAngle = player.aimAngle != null ? player.aimAngle : (player.team === 0 ? Math.PI / 2 : -Math.PI / 2);
    const breakdown = resolveShot(player, this.ball, shotType, aimAngle, this.rallyTime || 0);

    this.ball.isServe = false;
    this.ball.serveValidated = false;

    this.lastShotBreakdown = {
      base: Math.round(breakdown.base),
      fromBall: Math.round(breakdown.speedTransfer),
      fromMomentum: Math.round(breakdown.momentumBonus),
      rallyMult: breakdown.rallyMult.toFixed(2),
      intoShot: Math.round(breakdown.intoShot),
      playerSpeed: Math.round(breakdown.playerSpeed),
      total: Math.round(breakdown.finalSpeed),
    };
  }

  scorePoint(team) {
    if (!this.score || this.pointPauseTimer > 0) return;

    this.ball.state = 'dead';
    this.ball.vx = 0;
    this.ball.vy = 0;
    this.ball.vz = 0;
    this.serveState = 'none';

    const pointNames = ['0', '15', '30', '40'];
    this.score.points[team]++;

    if (this.score.points[team] >= 4) {
      this.score.games[team]++;
      this.score.points = [0, 0];
      
      this.servingTeam = this.servingTeam === 0 ? 1 : 0;
      this.serveSide = 'deuce';
      this.serveFaults = 0;
      this.showMessage(`Гейм — Команда ${team + 1}!`, 2);
    } else {
      
      this.serveSide = this.serveSide === 'deuce' ? 'ad' : 'deuce';
      this.serveFaults = 0;
      const p = this.score.points;
      this.showMessage(`${pointNames[p[0]]} - ${pointNames[p[1]]}`, 1.5);
    }

    this.score.servingTeam = this.servingTeam;
    this.pointPauseTimer = 2;
  }

  render() {
    const localPlayer = this.getLocalPlayer();

    let serveInfo = null;
    if (this.serveState === 'waiting' || this.serveState === 'tossed') {
      const isLocalServing = this.isLocalServing();
      const isTeammateServing = !isLocalServing && localPlayer != null &&
        this.servingTeam === localPlayer.team;
      serveInfo = {
        state: this.serveState,
        servingTeam: this.servingTeam,
        serveSide: this.serveSide,
        isLocalServing,
        isTeammateServing,
        faults: this.serveFaults,
        tossTimer: this.serveTossTimer,
        ballVz: this.ball.vz
      };
    }
    
    let timingInfo = null;
    if (this.serveTimingTimer > 0 && this.serveTiming) {
      timingInfo = { rating: this.serveTiming, timer: this.serveTimingTimer };
    }

    this.renderer.render({
      players: this.players,
      ball: this.ball,
      localPlayerId: this.localPlayerId,
      score: this.score,
      message: this.message,
      serveInfo,
      timingInfo,
      debug: {
        FPS: Math.round(1 / Math.max(0.001, (performance.now() - this.lastTime) / 1000 + 0.016)),
        Ball: `(${Math.round(this.ball.x)}, ${Math.round(this.ball.y)}, z:${Math.round(this.ball.z)})`,
        Speed: Math.round(Math.sqrt(this.ball.vx ** 2 + this.ball.vy ** 2 + this.ball.vz ** 2)),
        Bounces: this.ball.bounceCount,
        Serve: this.serveState,
        State: this.ball.state
      }
    });
  }

  showMessage(text, duration) {
    this.message = text;
    this.messageTimer = duration;
  }

  getLocalPlayer() {
    return this.players.find(p => p.id === this.localPlayerId);
  }

  stop() {
    this.running = false;
  }
}
