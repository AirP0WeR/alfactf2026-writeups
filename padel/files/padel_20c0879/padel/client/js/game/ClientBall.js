import { COURT_WIDTH, COURT_LENGTH } from '../../../shared/constants.js';
import { updateBallPhysics } from '../../../shared/BallPhysics.js';

export class ClientBall {
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
    this.state = 'dead';
    this.lastSide = null;
    this.isServe = false;
    this.serveValidated = false;

    this.hitTeam = null;
    this.needsCross = false;
    this.hitNet = false;
  }

  update(dt) {
    updateBallPhysics(this, dt);
  }

  applyServerState(serverBall) {
    this.x = serverBall.x;
    this.y = serverBall.y;
    this.z = serverBall.z;
    this.vx = serverBall.vx;
    this.vy = serverBall.vy;
    this.vz = serverBall.vz;
    this.state = serverBall.state || this.state;
    this.bounceCount = serverBall.bounceCount || 0;
    if (serverBall.spinX != null) this.spinX = serverBall.spinX;
    if (serverBall.spinY != null) this.spinY = serverBall.spinY;
    if (serverBall.hitTeam !== undefined) this.hitTeam = serverBall.hitTeam;
    if (serverBall.needsCross !== undefined) this.needsCross = serverBall.needsCross;
  }
}
