import { BallPhysics } from './BallPhysics.js';
import { CourtCollisions } from './CourtCollisions.js';
import { ShotResolver } from './ShotResolver.js';

export class PhysicsEngine {
  constructor() {
    this.ballPhysics = new BallPhysics();
    this.courtCollisions = new CourtCollisions();
    this.shotResolver = new ShotResolver();
  }

  update(ball, players, dt) {
    
    this.ballPhysics.update(ball, dt);

    this.courtCollisions.resolve(ball, dt);
  }

  tryShot(player, ball, shotModifier, aimAngle, rallyTime = 0) {
    return this.shotResolver.resolve(player, ball, shotModifier, aimAngle, rallyTime);
  }

  canPlayerHit(player, ball) {
    return this.shotResolver.canHit(player, ball);
  }
}
