import {
  PLAYER_MAX_SPEED, PLAYER_SPRINT_SPEED, PLAYER_ACCELERATION, PLAYER_DECELERATION,
  PLAYER_RADIUS, MAX_STAMINA, STAMINA_DRAIN, STAMINA_REGEN,
  COURT_WIDTH, COURT_LENGTH, NET_Y
} from '../../../shared/constants.js';

export class ClientPlayer {
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
    this.state = 'idle';
    this.swingTimer = 0;
    this.swingConnected = false;
    this.swingIsRally = false;
    this.pendingShotType = null;
    this.aimAngle = team === 0 ? Math.PI / 2 : -Math.PI / 2;
  }

  update(dt, input) {
    const dir = input.getMovementDir();
    const sprinting = input.isSprinting() && this.stamina > 0;
    const maxSpeed = sprinting ? PLAYER_SPRINT_SPEED : PLAYER_MAX_SPEED;

    if (sprinting && (dir.dx !== 0 || dir.dy !== 0)) {
      this.stamina = Math.max(0, this.stamina - STAMINA_DRAIN * dt);
    } else {
      this.stamina = Math.min(MAX_STAMINA, this.stamina + STAMINA_REGEN * dt);
    }

    if (dir.dx !== 0 || dir.dy !== 0) {
      this.vx += dir.dx * PLAYER_ACCELERATION * dt;
      this.vy += dir.dy * PLAYER_ACCELERATION * dt;
      this.state = 'moving';

      this.facing = Math.atan2(dir.dy, dir.dx);
      
      this.aimAngle = this.facing;
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
        this.state = 'idle';
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
  }

  applyServerState(serverPlayer) {
    
    this.x = serverPlayer.x;
    this.y = serverPlayer.y;
    this.vx = serverPlayer.vx || 0;
    this.vy = serverPlayer.vy || 0;
    this.stamina = serverPlayer.stamina != null ? serverPlayer.stamina : this.stamina;
    this.state = serverPlayer.state || this.state;
    this.facing = serverPlayer.facing != null ? serverPlayer.facing : this.facing;
  }
}
