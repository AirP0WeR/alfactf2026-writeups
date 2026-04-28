import {
  GRAVITY, BALL_DRAG, SPIN_FACTOR, MAX_BALL_SPEED,
  COURT_WIDTH, COURT_LENGTH, NET_Y, NET_HEIGHT, NET_POST_HEIGHT,
  BALL_RADIUS, BALL_BOUNCE_COEFF, WALL_BOUNCE_COEFF,
  BACK_WALL_HEIGHT, SIDE_WALL_GLASS_LENGTH, SIDE_WALL_GLASS_HEIGHT,
  FENCE_HEIGHT
} from './constants.js';

export function updateBallPhysics(ball, dt) {
  if (ball.state !== 'in_play') return;

  ball.vz -= GRAVITY * dt;

  const speed = Math.sqrt(ball.vx * ball.vx + ball.vy * ball.vy + ball.vz * ball.vz);
  const dragFactor = BALL_DRAG + speed * 0.000003;
  ball.vx *= (1 - dragFactor);
  ball.vy *= (1 - dragFactor);
  ball.vz *= (1 - dragFactor * 0.5);

  ball.vx += ball.spinY * SPIN_FACTOR * dt * 120;
  ball.vy += -ball.spinX * SPIN_FACTOR * dt * 80;
  ball.vz += -ball.spinX * SPIN_FACTOR * dt * 60;

  ball.spinX *= (1 - 0.3 * dt);
  ball.spinY *= (1 - 0.3 * dt);

  if (speed > MAX_BALL_SPEED) {
    const f = MAX_BALL_SPEED / speed;
    ball.vx *= f;
    ball.vy *= f;
    ball.vz *= f;
  }

  ball.x += ball.vx * dt;
  ball.y += ball.vy * dt;
  ball.z += ball.vz * dt;

  if (ball.needsCross && ball.hitTeam != null) {
    const currentSide = ball.y < NET_Y ? 0 : 1;
    if (currentSide !== ball.hitTeam) ball.needsCross = false;
  }

  resolveFloor(ball);
  resolveWalls(ball);
  resolveNet(ball, dt);
  resolveOutOfBounds(ball);
}

function resolveFloor(ball) {
  if (ball.z <= 0) {
    ball.z = 0;
    ball.vz = Math.abs(ball.vz) * BALL_BOUNCE_COEFF;

    const groundSpeed = Math.sqrt(ball.vx * ball.vx + ball.vy * ball.vy);
    const frictionFactor = groundSpeed > 800 ? 0.90 : 0.82;
    ball.vx *= frictionFactor;
    ball.vy *= frictionFactor;

    ball.vy += -ball.spinX * 50;
    ball.vx += ball.spinY * 40;

    if (ball.spinX < -0.2) {
      ball.vz += Math.abs(ball.spinX) * 40;
    }
    if (ball.spinX > 0.2) {
      ball.vz *= Math.max(0.6, 1 - ball.spinX * 0.3);
    }

    ball.spinX *= 0.35;
    ball.spinY *= 0.4;

    ball.bounceCount++;
    ball.lastSide = ball.y < NET_Y ? 0 : 1;

    if (ball.vz < 20) {
      ball.vz = 0;
    }
  }
}

function getSideWallHeight(y) {
  const distFromEnd = Math.min(y, COURT_LENGTH - y);
  if (distFromEnd <= SIDE_WALL_GLASS_LENGTH) {
    return SIDE_WALL_GLASS_HEIGHT;
  }
  return FENCE_HEIGHT;
}

function resolveWalls(ball) {
  const r = BALL_RADIUS;

  if (ball.x - r <= 0) {
    const wallH = getSideWallHeight(ball.y);
    if (ball.z < wallH) {
      ball.x = r;
      ball.vx = Math.abs(ball.vx) * WALL_BOUNCE_COEFF;
      ball.vy += ball.spinY * 15;
      ball.spinY *= -0.4;
    }
  }

  if (ball.x + r >= COURT_WIDTH) {
    const wallH = getSideWallHeight(ball.y);
    if (ball.z < wallH) {
      ball.x = COURT_WIDTH - r;
      ball.vx = -Math.abs(ball.vx) * WALL_BOUNCE_COEFF;
      ball.vy += ball.spinY * 15;
      ball.spinY *= -0.4;
    }
  }

  if (ball.y - r <= 0) {
    if (ball.z < BACK_WALL_HEIGHT) {
      ball.y = r;
      ball.vy = Math.abs(ball.vy) * WALL_BOUNCE_COEFF;
      ball.vx += ball.spinX * 15;
      ball.spinX *= -0.4;
    }
  }

  if (ball.y + r >= COURT_LENGTH) {
    if (ball.z < BACK_WALL_HEIGHT) {
      ball.y = COURT_LENGTH - r;
      ball.vy = -Math.abs(ball.vy) * WALL_BOUNCE_COEFF;
      ball.vx += ball.spinX * 15;
      ball.spinX *= -0.4;
    }
  }
}

function resolveNet(ball, dt) {
  const prevY = ball.y - ball.vy * dt;
  const crossedForward = prevY < NET_Y && ball.y >= NET_Y;
  const crossedBackward = prevY > NET_Y && ball.y <= NET_Y;

  if (crossedForward || crossedBackward) {
    const t = Math.abs(ball.x - COURT_WIDTH / 2) / (COURT_WIDTH / 2);
    const netH = NET_HEIGHT + (NET_POST_HEIGHT - NET_HEIGHT) * t;

    if (ball.z < netH) {
      ball.hitNet = true;
      ball.y = crossedForward ? NET_Y - BALL_RADIUS : NET_Y + BALL_RADIUS;
      ball.vy *= -0.25;
      ball.vx *= 0.4;
      ball.vz = Math.max(ball.vz, 30);
      ball.spinX = 0;
      ball.spinY = 0;
    }
  }
}

function resolveOutOfBounds(ball) {
  const margin = 200;
  if (ball.x < -margin || ball.x > COURT_WIDTH + margin ||
      ball.y < -margin || ball.y > COURT_LENGTH + margin) {
    ball.state = 'dead';
  }
}
