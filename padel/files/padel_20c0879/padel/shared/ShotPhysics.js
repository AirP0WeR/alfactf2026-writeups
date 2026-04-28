import {
  SHOT_PARAMS, COURT_WIDTH, COURT_LENGTH, NET_Y
} from './constants.js';

export function resolveShot(player, ball, shotType, aimAngle, rallyTime) {
  const params = SHOT_PARAMS[shotType] || SHOT_PARAMS.flat;
  const dir = player.team === 0 ? 1 : -1;
  const incomingSpeed = Math.sqrt(ball.vx * ball.vx + ball.vy * ball.vy);
  const playerSpeed = Math.sqrt(player.vx * player.vx + player.vy * player.vy);

  const angle = aimAngle != null ? aimAngle : (player.team === 0 ? Math.PI / 2 : -Math.PI / 2);
  const aimDx = Math.cos(angle);
  const aimDy = Math.sin(angle);

  const aimingBackward = (player.team === 0 && aimDy < -0.3) || (player.team === 1 && aimDy > 0.3);

  let targetX = ball.x + aimDx * 800;
  let targetY = ball.y + aimDy * 800;

  if (shotType === 'angled' || shotType === 'angle_left') {
    targetX = COURT_WIDTH * 0.08 + Math.random() * COURT_WIDTH * 0.1;
    targetY = player.team === 0 ? COURT_LENGTH * 0.7 : COURT_LENGTH * 0.3;
  } else if (shotType === 'angle_right') {
    targetX = COURT_WIDTH * 0.82 + Math.random() * COURT_WIDTH * 0.1;
    targetY = player.team === 0 ? COURT_LENGTH * 0.7 : COURT_LENGTH * 0.3;
  } else if (shotType === 'lob' && !aimingBackward) {
    targetY = player.team === 0 ? COURT_LENGTH * 0.85 : COURT_LENGTH * 0.15;
  }

  targetX += (Math.random() - 0.5) * 60;
  targetY += (Math.random() - 0.5) * 40;
  targetX = Math.max(10, Math.min(COURT_WIDTH - 10, targetX));
  targetY = Math.max(10, Math.min(COURT_LENGTH - 10, targetY));

  const dx = targetX - ball.x;
  const dy = targetY - ball.y;
  const dist = Math.sqrt(dx * dx + dy * dy);

  const speedTransfer = Math.min(incomingSpeed * 0.25, 600);
  const intoShot = Math.max(-0.5, player.vx * aimDx + player.vy * aimDy);
  const momentumBonus = intoShot * 0.5 + playerSpeed * 0.03;

  const rallyMult = Math.min(1.3, 1.0 + (rallyTime || 0) * 0.15);
  let finalSpeed = Math.min((params.speed + speedTransfer + momentumBonus) * rallyMult, 3600);
  if (aimingBackward) finalSpeed = Math.min(finalSpeed * 1.2, 3600);

  const lateralRatio = Math.abs(dx) / (Math.abs(dx) + Math.abs(dy) + 1);
  ball.vx = (dx / dist) * finalSpeed * (0.3 + lateralRatio * 0.4);
  ball.vy = (dy / dist) * finalSpeed;

  let vz = params.vz;
  if (aimingBackward) {
    vz = Math.max(vz, 450);
  } else {
    // High ball preference: try to hit downward (smash-like), but net clearance can override
    if (ball.z > 180 && shotType !== 'lob') vz = Math.min(vz, -80);

    const distToNet = Math.abs(ball.y - NET_Y);
    // Account for drag slowing the ball — effective vy is ~85% of initial over the flight
    const effectiveVy = Math.abs(ball.vy) * 0.85 + 1;
    const timeToNet = distToNet / effectiveVy;
    const minVzForNet = (95 - ball.z + 0.5 * 980 * timeToNet * timeToNet) / (timeToNet + 0.01);
    if (shotType !== 'smash' && vz < minVzForNet) {
      vz = Math.min(minVzForNet + 15, 440);
    }
  }
  if (ball.z < 20 && ball.bounceCount > 0) vz = Math.max(vz, 300);
  ball.vz = vz;

  ball.spinX = params.spin + (player.vy * 0.0004 * -dir);
  ball.spinY = player.vx * 0.0008;

  ball.bounceCount = 0;
  ball.lastHitBy = player.id;
  ball.hitTeam = player.team;
  ball.needsCross = true;
  ball.hitNet = false;

  player.facing = Math.atan2(dy, dx);

  return { finalSpeed, speedTransfer, momentumBonus, rallyMult, intoShot, playerSpeed, base: params.speed };
}
