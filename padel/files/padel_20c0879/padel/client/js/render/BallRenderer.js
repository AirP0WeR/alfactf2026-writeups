import { BALL_RADIUS, COLORS } from '../../../shared/constants.js';

export class BallRenderer {
  constructor(camera) {
    this.camera = camera;
    this.ctx = camera.ctx;
    this.trail = [];
    this.maxTrail = 10;
  }

  draw(ball) {
    if (!ball) return;

    const { ctx, camera } = this;
    const pos = camera.toScreen(ball.x, ball.y);
    const z = ball.z || 0;
    
    const r = camera.toScreenDist(BALL_RADIUS * 3);

    const ballScreenY = pos.y - camera.toScreenDist(z * 0.35);
    this.trail.push({ x: pos.x, y: ballScreenY });
    if (this.trail.length > this.maxTrail) this.trail.shift();

    for (let i = 0; i < this.trail.length - 1; i++) {
      const t = i / this.trail.length;
      const alpha = t * 0.35;
      ctx.fillStyle = `rgba(220, 250, 80, ${alpha})`;
      ctx.beginPath();
      ctx.arc(this.trail[i].x, this.trail[i].y, r * (0.25 + t * 0.4), 0, Math.PI * 2);
      ctx.fill();
    }

    const shadowScale = Math.max(0.25, 1 - z / 400);
    const shadowAlpha = Math.max(0.12, 0.5 - z / 900);
    const shadowOffset = camera.toScreenDist(z * 0.2);
    const sx = pos.x;
    const sy = pos.y + shadowOffset;
    const srx = r * shadowScale * 1.3;
    const sry = r * shadowScale * 0.75;

    const shadowGrad = ctx.createRadialGradient(sx, sy, 0, sx, sy, srx);
    shadowGrad.addColorStop(0, `rgba(0, 0, 0, ${shadowAlpha})`);
    shadowGrad.addColorStop(0.7, `rgba(0, 0, 0, ${shadowAlpha * 0.5})`);
    shadowGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = shadowGrad;
    ctx.beginPath();
    ctx.ellipse(sx, sy, srx, sry, 0, 0, Math.PI * 2);
    ctx.fill();

    if (z > 15) {
      ctx.strokeStyle = `rgba(200, 230, 32, ${Math.min(0.4, z / 300)})`;
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 3]);
      ctx.beginPath();
      ctx.moveTo(pos.x, pos.y);
      ctx.lineTo(pos.x, ballScreenY);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    const ballScale = 1 + z / 1000;
    const rb = r * ballScale;

    const glow = ctx.createRadialGradient(pos.x, ballScreenY, rb * 0.9, pos.x, ballScreenY, rb * 2);
    glow.addColorStop(0, 'rgba(220, 255, 60, 0.45)');
    glow.addColorStop(1, 'rgba(220, 255, 60, 0)');
    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(pos.x, ballScreenY, rb * 2, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.beginPath();
    ctx.arc(pos.x, ballScreenY + 1, rb * 1.12, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.lineWidth = Math.max(2, rb * 0.12);
    ctx.beginPath();
    ctx.arc(pos.x, ballScreenY, rb * 1.05, 0, Math.PI * 2);
    ctx.stroke();

    const bg = ctx.createRadialGradient(
      pos.x - rb * 0.35, ballScreenY - rb * 0.4, rb * 0.1,
      pos.x, ballScreenY, rb
    );
    bg.addColorStop(0, '#ffffc0');
    bg.addColorStop(0.4, '#e4ff32');
    bg.addColorStop(1, '#5e7a00');
    ctx.fillStyle = bg;
    ctx.beginPath();
    ctx.arc(pos.x, ballScreenY, rb, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.75)';
    ctx.lineWidth = Math.max(1, rb * 0.12);
    ctx.beginPath();
    ctx.arc(pos.x, ballScreenY + rb * 0.2, rb * 0.9, Math.PI * 1.05, Math.PI * 1.95);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(pos.x, ballScreenY - rb * 0.2, rb * 0.9, Math.PI * 0.05, Math.PI * 0.95);
    ctx.stroke();

    const hg = ctx.createRadialGradient(
      pos.x - rb * 0.3, ballScreenY - rb * 0.35, 0,
      pos.x - rb * 0.3, ballScreenY - rb * 0.35, rb * 0.6
    );
    hg.addColorStop(0, 'rgba(255, 255, 255, 0.65)');
    hg.addColorStop(1, 'rgba(255, 255, 255, 0)');
    ctx.fillStyle = hg;
    ctx.beginPath();
    ctx.arc(pos.x - rb * 0.3, ballScreenY - rb * 0.35, rb * 0.6, 0, Math.PI * 2);
    ctx.fill();
  }
}
