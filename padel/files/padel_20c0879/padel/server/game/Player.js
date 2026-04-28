import {
  PLAYER_MAX_SPEED, PLAYER_SPRINT_SPEED, PLAYER_ACCELERATION, PLAYER_DECELERATION,
  PLAYER_RADIUS, MAX_STAMINA, STAMINA_DRAIN, STAMINA_REGEN,
  COURT_WIDTH, COURT_LENGTH, NET_Y, PLAYER_STATES
} from '../../shared/constants.js';

export class Player {
  constructor(id, team, x, y, name) {
    this.id = id;
    this.team = team;
    this.x = x;
    this.y = y;
    this.vx = 0;
    this.vy = 0;
    this.facing = team === 0 ? Math.PI / 2 : -Math.PI / 2;
    this.stamina = MAX_STAMINA;
    this.name = name || 'Player';
    this.state = PLAYER_STATES.IDLE;
    this.swingTimer = 0;
    this.ws = null;
    this.rtt = 0;
    this.lastInput = null;
  }

  applyInput(input, dt) {
    let dx = 0, dy = 0;
    if (input.left) dx -= 1;
    if (input.right) dx += 1;
    if (input.up) dy += 1;
    if (input.down) dy -= 1;

    if (dx !== 0 && dy !== 0) {
      const inv = 1 / Math.SQRT2;
      dx *= inv;
      dy *= inv;
    }

    const sprinting = input.sprint && this.stamina > 0;
    const maxSpeed = sprinting ? PLAYER_SPRINT_SPEED : PLAYER_MAX_SPEED;

    if (sprinting && (dx !== 0 || dy !== 0)) {
      this.stamina = Math.max(0, this.stamina - STAMINA_DRAIN * dt);
    } else {
      this.stamina = Math.min(MAX_STAMINA, this.stamina + STAMINA_REGEN * dt);
    }

    if (dx !== 0 || dy !== 0) {
      this.vx += dx * PLAYER_ACCELERATION * dt;
      this.vy += dy * PLAYER_ACCELERATION * dt;
      this.state = PLAYER_STATES.MOVING;
      this.facing = Math.atan2(dy, dx);
    } else {
      const speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
      if (speed > 0) {
        const decel = Math.min(speed, PLAYER_DECELERATION * dt);
        const factor = (speed - decel) / speed;
        this.vx *= factor;
        this.vy *= factor;
      }
      if (speed < 10) {
        this.vx = 0;
        this.vy = 0;
        this.state = PLAYER_STATES.IDLE;
      }
    }

    const speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
    if (speed > maxSpeed) {
      this.vx = (this.vx / speed) * maxSpeed;
      this.vy = (this.vy / speed) * maxSpeed;
    }

    this.x += this.vx * dt;
    this.y += this.vy * dt;

    const r = PLAYER_RADIUS;
    this.x = Math.max(r, Math.min(COURT_WIDTH - r, this.x));
    if (this.team === 0) {
      this.y = Math.max(r, Math.min(NET_Y - r, this.y));
    } else {
      this.y = Math.max(NET_Y + r, Math.min(COURT_LENGTH - r, this.y));
    }

    if (this.swingTimer > 0) {
      this.swingTimer -= dt * 1000;
      if (this.swingTimer <= 0) {
        this.swingTimer = 0;
        if (this.state === PLAYER_STATES.SWINGING) {
          this.state = PLAYER_STATES.IDLE;
        }
      }
    }
  }

  serialize() {
    return {
      id: this.id,
      team: this.team,
      x: Math.round(this.x),
      y: Math.round(this.y),
      vx: Math.round(this.vx),
      vy: Math.round(this.vy),
      facing: Math.round(this.facing * 100) / 100,
      stamina: Math.round(this.stamina),
      state: this.state,
      name: this.name
    };
  }
}
