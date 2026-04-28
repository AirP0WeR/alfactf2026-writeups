import {
  COURT_WIDTH, COURT_LENGTH, BALL_STATES
} from '../../shared/constants.js';

export class Ball {
  constructor() {
    this.reset();
  }

  reset() {
    this.x = COURT_WIDTH / 2;
    this.y = COURT_LENGTH / 2;
    this.z = 100;
    this.vx = 0;
    this.vy = 0;
    this.vz = 0;
    this.spinX = 0;
    this.spinY = 0;
    this.spinZ = 0;
    this.bounceCount = 0;
    this.lastHitBy = null;
    this.state = BALL_STATES.DEAD;
    this.lastSide = null;
    this.hitNet = false;
    
    this.hitTeam = null;
    this.needsCross = false;
  }

  serialize() {
    return {
      x: Math.round(this.x * 10) / 10,
      y: Math.round(this.y * 10) / 10,
      z: Math.round(this.z * 10) / 10,
      vx: Math.round(this.vx),
      vy: Math.round(this.vy),
      vz: Math.round(this.vz),
      spinX: Math.round(this.spinX * 100) / 100,
      spinY: Math.round(this.spinY * 100) / 100,
      state: this.state,
      bounceCount: this.bounceCount,
      lastHitBy: this.lastHitBy,
      hitTeam: this.hitTeam,
      needsCross: this.needsCross
    };
  }
}
