import { Ball } from './game/Ball.js';
import { ScoringSystem } from './game/ScoringSystem.js';
import { ServeManager } from './game/ServeManager.js';
import { RulesEngine } from './game/RulesEngine.js';
import { GAME_STATES, BALL_STATES, COURT_WIDTH, COURT_LENGTH, NET_Y, SERVICE_LINE_DIST, CENTER_SERVICE_X } from '../shared/constants.js';

export class GameState {
  constructor() {
    this.ball = new Ball();
    this.scoring = new ScoringSystem();
    this.serveManager = new ServeManager();
    this.rules = new RulesEngine();
    this.state = GAME_STATES.WAITING;
    this.pointPauseTimer = 0;
    this.tick = 0;
    this.rallyTime = 0;
  }

  reset() {
    this.ball.reset();
    this.scoring.reset();
    this.state = GAME_STATES.WAITING;
    this.tick = 0;
  }

  startMatch() {
    this.state = GAME_STATES.SERVING;
    this.scoring.reset();
    this.serveManager.setupServe(0, 0, 'deuce');
    this.setupServe();
  }

  setupServe() {
    this.state = GAME_STATES.SERVING;
    this.servePhase = 'waiting';
    this.serveTossTimer = 0;
    this.rallyTime = 0;
    
    this.ball.vx = 0;
    this.ball.vy = 0;
    this.ball.vz = 0;
    this.ball.state = BALL_STATES.SERVING;
    this.ball.bounceCount = 0;
    this.ball.hitNet = false;
    
    this.ball.hitTeam = null;
    this.ball.needsCross = false;
    this.ball.lastHitBy = null;
  }

  updateServe(servingPlayer, dt) {
    if (this.state !== GAME_STATES.SERVING || !servingPlayer) return;
    const dir = servingPlayer.team === 0 ? 1 : -1;

    if (this.servePhase === 'waiting') {
      
      this.ball.x = servingPlayer.x + (servingPlayer.team === 0 ? 15 : -15);
      this.ball.y = servingPlayer.y;
      this.ball.z = 70;
      this.ball.vx = 0;
      this.ball.vy = 0;
      this.ball.vz = 0;
    } else if (this.servePhase === 'tossed') {
      this.serveTossTimer += dt;
      
      this.ball.x = servingPlayer.x + (servingPlayer.team === 0 ? 15 : -15);
      this.ball.y = servingPlayer.y + dir * this.serveTossTimer * 30;
      
      this.ball.vz -= 980 * dt;
      this.ball.z += this.ball.vz * dt;

      if (this.ball.z <= 0 && this.serveTossTimer > 0.15) {
        this.ball.z = 0;
        this.ball.vz = 0;
        return 'drop_fault';
      }
    }
    return null;
  }

  serveToss() {
    if (this.state !== GAME_STATES.SERVING || this.servePhase !== 'waiting') return false;
    this.servePhase = 'tossed';
    this.serveTossTimer = 0;
    this.ball.vz = 500;
    return true;
  }

  serveHit(servingPlayer, aimAngle) {
    if (this.state !== GAME_STATES.SERVING || this.servePhase !== 'tossed') return false;
    if (this.serveTossTimer < 0.12 || this.ball.z < 20) return false;

    const dir = servingPlayer.team === 0 ? 1 : -1;

    const peakProximity = Math.abs(this.ball.vz);
    let powerMult = 0.7, accuracySpread = 120;
    if (peakProximity < 40) { powerMult = 1.0; accuracySpread = 40; }
    else if (peakProximity < 120) { powerMult = 0.85; accuracySpread = 70; }
    else if (this.ball.vz > 0) { powerMult = 0.65; accuracySpread = 130; }
    else { powerMult = 0.6; accuracySpread = 150; }

    const side = this.serveManager.serveSide;
    let boxMinX, boxMaxX, boxMinY, boxMaxY;
    if (servingPlayer.team === 0) {
      boxMinY = NET_Y; boxMaxY = NET_Y + SERVICE_LINE_DIST;
      if (side === 'deuce') { boxMinX = 0; boxMaxX = CENTER_SERVICE_X; }
      else { boxMinX = CENTER_SERVICE_X; boxMaxX = COURT_WIDTH; }
    } else {
      boxMinY = NET_Y - SERVICE_LINE_DIST; boxMaxY = NET_Y;
      if (side === 'deuce') { boxMinX = CENTER_SERVICE_X; boxMaxX = COURT_WIDTH; }
      else { boxMinX = 0; boxMaxX = CENTER_SERVICE_X; }
    }

    const angle = aimAngle != null ? aimAngle : (servingPlayer.team === 0 ? Math.PI / 2 : -Math.PI / 2);
    const aimDx = Math.cos(angle);
    const aimDy = Math.sin(angle);
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

    const baseSpeed = 3000 + Math.random() * 800;
    const speed = baseSpeed * powerMult;

    this.ball.vx = (dx / dist) * speed * 0.3;
    this.ball.vy = (dy / dist) * speed;

    const g = 980;
    const netClearance = 170;
    const distToNet = Math.abs(NET_Y - this.ball.y);
    const tToTarget = Math.max(0.1, dist / speed);
    const tToNet = Math.max(0.05, distToNet / speed);
    const ballisticVz = (0.5 * g * tToTarget * tToTarget - this.ball.z) / tToTarget;
    const netVz = (netClearance - this.ball.z + 0.5 * g * tToNet * tToNet) / tToNet;
    this.ball.vz = Math.max(ballisticVz, netVz);
    this.ball.spinX = dir * (0.15 + powerMult * 0.15);
    this.ball.spinY = 0;
    this.ball.bounceCount = 0;
    this.ball.state = BALL_STATES.IN_PLAY;
    this.ball.lastHitBy = servingPlayer.id;
    this.ball.hitNet = false;
    
    this.ball.hitTeam = null;
    this.ball.needsCross = false;

    this.state = GAME_STATES.PLAYING;
    this.servePhase = null;
    return true;
  }

  handlePointScored(team) {
    this.ball.state = BALL_STATES.DEAD;
    this.state = GAME_STATES.POINT_SCORED;
    this.pointPauseTimer = 2000;

    const result = this.scoring.scorePoint(team);
    return result;
  }

  updatePointPause(dt) {
    if (this.state !== GAME_STATES.POINT_SCORED) return false;

    this.pointPauseTimer -= dt * 1000;
    if (this.pointPauseTimer <= 0) {
      if (this.scoring.matchOver) {
        this.state = GAME_STATES.MATCH_ENDED;
        return true;
      }

      this.serveManager.nextPoint();
      this.serveManager.servingTeam = this.scoring.servingTeam;
      this.serveManager.servingPlayerIndex = this.scoring.servingPlayerIndex;
      this.setupServe();
      return true;
    }
    return false;
  }

  serialize() {
    return {
      tick: this.tick,
      ball: this.ball.serialize(),
      score: this.scoring.serialize(),
      state: this.state,
      servePhase: this.servePhase || null,
      servingTeam: this.serveManager.servingTeam,
      serveSide: this.serveManager.serveSide,
      serveFaults: this.serveManager.faults
    };
  }
}
