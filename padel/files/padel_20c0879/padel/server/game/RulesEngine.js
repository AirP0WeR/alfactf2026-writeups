import {
  COURT_WIDTH, COURT_LENGTH, NET_Y, BALL_STATES
} from '../../shared/constants.js';

export class RulesEngine {
  constructor() {
    this.pointResult = null;
  }

  evaluate(ball, players, gameState) {
    this.pointResult = null;

    if (ball.state !== BALL_STATES.IN_PLAY) return null;

    if (ball.needsCross && ball.bounceCount >= 1 &&
        ball.hitTeam != null && ball.lastSide === ball.hitTeam && !ball.isServe) {
      const scoringTeam = ball.hitTeam === 0 ? 1 : 0;
      this.pointResult = {
        team: scoringTeam,
        reason: 'no_cross'
      };
      return this.pointResult;
    }

    if (ball.bounceCount >= 2) {
      const scoringTeam = ball.lastSide === 0 ? 1 : 0;
      this.pointResult = {
        team: scoringTeam,
        reason: 'double_bounce'
      };
      return this.pointResult;
    }

    if (this.isBallOut(ball)) {
      
      const lastHitter = players.find(p => p.id === ball.lastHitBy);
      if (lastHitter) {
        const scoringTeam = lastHitter.team === 0 ? 1 : 0;
        this.pointResult = {
          team: scoringTeam,
          reason: 'out'
        };
        return this.pointResult;
      }
    }

    if (ball.z <= 0 && Math.abs(ball.vz) < 5 &&
        Math.abs(ball.vx) < 10 && Math.abs(ball.vy) < 10 &&
        ball.bounceCount >= 1) {
      const scoringTeam = ball.y < NET_Y ? 1 : 0;
      this.pointResult = {
        team: scoringTeam,
        reason: 'ball_stopped'
      };
      return this.pointResult;
    }

    return null;
  }

  isBallOut(ball) {
    
    const margin = 100;
    return ball.x < -margin || ball.x > COURT_WIDTH + margin ||
           ball.y < -margin || ball.y > COURT_LENGTH + margin;
  }

  evaluateServe(ball, serveManager) {
    if (ball.bounceCount === 0) return 'pending';

    const box = serveManager.getTargetBox();

    if (ball.bounceCount >= 1) {
      const inBox = ball.x >= box.x1 && ball.x <= box.x2 &&
                    ball.y >= box.y1 && ball.y <= box.y2;

      if (!inBox) {
        return 'fault';
      }

      return 'good';
    }

    return 'pending';
  }
}
