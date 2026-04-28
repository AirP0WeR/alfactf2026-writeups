import {
  COURT_WIDTH, COURT_LENGTH, NET_Y, SHOT_REACH,
  PLAYER_MAX_SPEED, BALL_STATES, GAME_STATES, PLAYER_STATES,
} from '../../shared/constants.js';

const BOT_HIT_REACH = SHOT_REACH * 0.55;

export class BotController {
  constructor(player) {
    this.player = player;
    this.reactionJitter = Math.random() * 0.15;
    this.serveWaitTimer = 0;

    this.zoneSide = player.x < COURT_WIDTH / 2 ? -1 : +1;

    this.homeX = this.zoneSide < 0 ? COURT_WIDTH * 0.28 : COURT_WIDTH * 0.72;
    this.homeY = player.team === 0
      ? COURT_LENGTH * 0.2
      : COURT_LENGTH * 0.8;

    this.aggression = 0.4 + Math.random() * 0.5;
  }

  tick(gameState, ball, physics, rallyTime, dt, players) {
    const bot = this.player;

    if (bot.swingTimer > 0) {
      bot.swingTimer -= dt * 1000;
      if (bot.swingTimer <= 0) {
        bot.swingTimer = 0;
        if (bot.state === PLAYER_STATES.SWINGING) {
          bot.state = PLAYER_STATES.IDLE;
        }
      }
    }

    if (gameState.state === GAME_STATES.SERVING) {
      const isMyServe = this._isServingPlayer;
      if (!isMyServe) {
        this._moveToward(this._homePosition(), dt);
        return;
      }

      const serveSide = gameState.serveManager.serveSide;
      let serveX;
      if (bot.team === 0) {
        serveX = serveSide === 'deuce' ? COURT_WIDTH * 0.75 : COURT_WIDTH * 0.25;
      } else {
        serveX = serveSide === 'deuce' ? COURT_WIDTH * 0.25 : COURT_WIDTH * 0.75;
      }
      const serveY = bot.team === 0 ? 150 : COURT_LENGTH - 150;

      if (gameState.servePhase === 'waiting') {
        const dx = serveX - bot.x;
        const dy = serveY - bot.y;
        const inPosition = Math.hypot(dx, dy) < 20;

        if (!inPosition) {
          this._moveToward({ x: serveX, y: serveY }, dt);
          this.serveWaitTimer = 0;
          return;
        }

        bot.vx = 0;
        bot.vy = 0;
        if (bot.state !== PLAYER_STATES.SWINGING) bot.state = PLAYER_STATES.IDLE;

        this.serveWaitTimer += dt;
        if (this.serveWaitTimer > 0.8 + this.reactionJitter) {
          gameState.serveToss();
          this.serveWaitTimer = 0;
        }
        return;
      }

      if (gameState.servePhase === 'tossed' && gameState.serveTossTimer >= 0.6) {
        
        const base = bot.team === 0 ? Math.PI / 2 : -Math.PI / 2;
        const wobble = (Math.random() - 0.5) * 0.3;
        gameState.serveHit(bot, base + wobble);
      }
      return;
    }

    if (ball.state === BALL_STATES.DEAD) {
      this._moveToward(this._homePosition(), dt);
      return;
    }

    let predictedX = ball.x;
    let predictedY = ball.y;
    let leadT = 0.3;
    if (Math.abs(ball.vy) > 50) {
      const t = (bot.y - ball.y) / ball.vy;
      if (t > 0.05 && t < 1.5) leadT = t;
    }
    predictedX = ball.x + ball.vx * leadT;
    predictedY = ball.y + ball.vy * leadT;

    const shouldChase = this._shouldChase(predictedX, predictedY, players);

    let targetX;
    let targetY;
    if (shouldChase) {
      targetX = predictedX;
      targetY = predictedY;
    } else {
      
      targetX = this.homeX * 0.6 + predictedX * 0.4;
      targetY = this.homeY;
    }

    if (bot.team === 1) {
      targetY = Math.max(NET_Y + 50, Math.min(COURT_LENGTH - 30, targetY));
    } else {
      targetY = Math.max(30, Math.min(NET_Y - 50, targetY));
    }
    targetX = Math.max(30, Math.min(COURT_WIDTH - 30, targetX));

    this._moveToward({ x: targetX, y: targetY }, dt);

    const botBlockedByOwnHit = ball.hitTeam === bot.team;
    if (ball.state === BALL_STATES.IN_PLAY && bot.swingTimer <= 0 && !botBlockedByOwnHit) {
      const ballDist = Math.hypot(bot.x - ball.x, bot.y - ball.y);
      if (ballDist < BOT_HIT_REACH && ball.z < 300) {
        const { shotType, aimAngle } = this._pickShot(ball);
        physics.tryShot(bot, ball, shotType, aimAngle, rallyTime);
      }
    }
  }

  _shouldChase(predictedX, predictedY, players) {
    if (!players) return true;
    const bot = this.player;

    const ballSide = predictedX < COURT_WIDTH / 2 ? -1 : +1;
    const myDist = Math.hypot(bot.x - predictedX, bot.y - predictedY);

    let partner = null;
    for (const other of players.values()) {
      if (other === bot) continue;
      if (other.team !== bot.team) continue;
      partner = other;
      break;
    }

    if (!partner) return true;

    const partnerDist = Math.hypot(partner.x - predictedX, partner.y - predictedY);

    if (ballSide === this.zoneSide) {
      return myDist < partnerDist + 200;
    }

    return myDist + 150 < partnerDist;
  }

  _pickShot(ball) {
    const bot = this.player;
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
      target = this.zoneSide < 0 ? leftCorner : rightCorner;
    } else {
      const roll = Math.random();
      if (roll < 0.18) {
        
        shotType = 'lob';
        target = deepMiddle;
      } else if (roll < 0.38 * this.aggression) {
        
        shotType = 'angled';
        target = this.zoneSide < 0 ? leftCorner : rightCorner;
        target = { x: target.x, y: bot.team === 0 ? NET_Y + 180 : NET_Y - 180 };
      } else if (roll < 0.7) {
        
        shotType = Math.random() < 0.35 ? 'angled' : 'flat';
        target = this.zoneSide < 0 ? rightCorner : leftCorner;
      } else if (roll < 0.9) {
        
        shotType = 'flat';
        target = this.zoneSide < 0 ? leftCorner : rightCorner;
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

  _homePosition() {
    return { x: this.homeX, y: this.homeY };
  }

  _moveToward(target, dt) {
    const bot = this.player;
    const dx = target.x - bot.x;
    const dy = target.y - bot.y;
    const dist = Math.hypot(dx, dy);

    if (dist > 15) {
      const speed = PLAYER_MAX_SPEED;
      bot.vx = (dx / dist) * speed;
      bot.vy = (dy / dist) * speed;
      bot.x += bot.vx * dt;
      bot.y += bot.vy * dt;
      bot.facing = Math.atan2(dy, dx);
      if (bot.state !== PLAYER_STATES.SWINGING) {
        bot.state = PLAYER_STATES.MOVING;
      }
    } else {
      bot.vx = 0;
      bot.vy = 0;
      if (bot.state !== PLAYER_STATES.SWINGING) {
        bot.state = PLAYER_STATES.IDLE;
      }
    }

    bot.x = Math.max(20, Math.min(COURT_WIDTH - 20, bot.x));
    if (bot.team === 1) {
      bot.y = Math.max(NET_Y + 20, Math.min(COURT_LENGTH - 20, bot.y));
    } else {
      bot.y = Math.max(20, Math.min(NET_Y - 20, bot.y));
    }
  }
}
