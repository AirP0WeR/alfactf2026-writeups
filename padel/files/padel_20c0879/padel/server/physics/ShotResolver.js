import {
  SHOT_REACH, SHOT_TYPES, SWING_TOTAL,
  PLAYER_STATES, BALL_STATES
} from '../../shared/constants.js';
import { resolveShot } from '../../shared/ShotPhysics.js';

export class ShotResolver {
  canHit(player, ball) {
    if (player.state === PLAYER_STATES.SWINGING) return false;
    if (ball.state !== BALL_STATES.IN_PLAY) return false;

    if (ball.hitTeam === player.team) return false;

    const dx = ball.x - player.x;
    const dy = ball.y - player.y;
    const dist = Math.sqrt(dx * dx + dy * dy);

    return dist <= SHOT_REACH && ball.z < 300;
  }

  resolve(player, ball, shotModifier, aimAngle, rallyTime = 0) {
    if (!this.canHit(player, ball)) return false;

    const shotType = this.determineShotType(shotModifier, ball);

    player.state = PLAYER_STATES.SWINGING;
    player.swingTimer = SWING_TOTAL;

    resolveShot(player, ball, shotType, aimAngle, rallyTime);

    return true;
  }

  determineShotType(modifier, ball) {

    if (!modifier) return SHOT_TYPES.FLAT;
    return modifier;
  }
}
