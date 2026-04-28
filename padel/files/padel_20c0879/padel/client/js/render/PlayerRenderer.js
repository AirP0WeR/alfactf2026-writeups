import { PLAYER_RADIUS, PADDLE_LENGTH, COLORS, MAX_STAMINA } from '../../../shared/constants.js';

export class PlayerRenderer {
  constructor(camera) {
    this.camera = camera;
    this.ctx = camera.ctx;
  }

  draw(player, isLocal) {
    const { ctx, camera } = this;
    const pos = camera.toScreen(player.x, player.y);
    const r = camera.toScreenDist(PLAYER_RADIUS);
    const teamColor = player.team === 0 ? COLORS.TEAM1 : COLORS.TEAM2;
    const darkColor = player.team === 0 ? '#7a1520' : '#203e57';

    const shadowGrad = ctx.createRadialGradient(
      pos.x + 3, pos.y + 5, 0,
      pos.x + 3, pos.y + 5, r * 1.6
    );
    shadowGrad.addColorStop(0, 'rgba(0,0,0,0.45)');
    shadowGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = shadowGrad;
    ctx.beginPath();
    ctx.ellipse(pos.x + 3, pos.y + 5, r * 1.4, r * 0.85, 0, 0, Math.PI * 2);
    ctx.fill();

    const bodyGrad = ctx.createRadialGradient(
      pos.x - r * 0.4, pos.y - r * 0.4, r * 0.1,
      pos.x, pos.y, r
    );
    bodyGrad.addColorStop(0, this.lighten(teamColor, 0.4));
    bodyGrad.addColorStop(0.55, teamColor);
    bodyGrad.addColorStop(1, darkColor);
    ctx.fillStyle = bodyGrad;
    ctx.strokeStyle = COLORS.PLAYER_OUTLINE;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, r, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = 'rgba(255,255,255,0.25)';
    ctx.beginPath();
    ctx.ellipse(pos.x - r * 0.25, pos.y - r * 0.45, r * 0.45, r * 0.2, 0, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = this.lighten(teamColor, 0.55);
    ctx.lineWidth = Math.max(1, camera.toScreenDist(3));
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, r * 0.6, 0, Math.PI * 2);
    ctx.stroke();

    const aimForPaddle = player.aimAngle != null ? player.aimAngle : (player.facing || 0);
    const paddleAngle = aimForPaddle - Math.PI / 2;
    const paddleLen = camera.toScreenDist(PADDLE_LENGTH);
    const px = pos.x + Math.cos(paddleAngle) * (r + 2);
    const py = pos.y - Math.sin(paddleAngle) * (r + 2);
    const pex = pos.x + Math.cos(paddleAngle) * (r + paddleLen);
    const pey = pos.y - Math.sin(paddleAngle) * (r + paddleLen);

    ctx.strokeStyle = 'rgba(0,0,0,0.5)';
    ctx.lineWidth = Math.max(4, camera.toScreenDist(8));
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(px + 1, py + 2);
    ctx.lineTo(pex + 1, pey + 2);
    ctx.stroke();

    ctx.strokeStyle = '#dcdcdc';
    ctx.lineWidth = Math.max(3, camera.toScreenDist(6));
    ctx.beginPath();
    ctx.moveTo(px, py);
    ctx.lineTo(pex, pey);
    ctx.stroke();

    ctx.strokeStyle = '#1b1b1b';
    ctx.lineWidth = Math.max(3, camera.toScreenDist(7));
    const gripMidX = px + (pex - px) * 0.18;
    const gripMidY = py + (pey - py) * 0.18;
    ctx.beginPath();
    ctx.moveTo(px, py);
    ctx.lineTo(gripMidX, gripMidY);
    ctx.stroke();

    const headR = camera.toScreenDist(11);
    const headGrad = ctx.createRadialGradient(
      pex - headR * 0.3, pey - headR * 0.3, 0,
      pex, pey, headR
    );
    headGrad.addColorStop(0, '#ffffff');
    headGrad.addColorStop(0.6, '#d0d0d0');
    headGrad.addColorStop(1, '#6a6a6a');
    ctx.fillStyle = headGrad;
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(pex, pey, headR, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = 'rgba(30,30,30,0.6)';
    for (let i = 0; i < 5; i++) {
      const ang = (i / 5) * Math.PI * 2;
      const ddx = pex + Math.cos(ang) * headR * 0.45;
      const ddy = pey + Math.sin(ang) * headR * 0.45;
      ctx.beginPath();
      ctx.arc(ddx, ddy, Math.max(1, headR * 0.12), 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.textAlign = 'center';

    if (isLocal && player.aimAngle != null) {
      const aimLen = camera.toScreenDist(80);
      const aimAngle = player.aimAngle;
      const ax = pos.x + Math.cos(aimAngle) * (r + 10);
      const ay = pos.y - Math.sin(aimAngle) * (r + 10);
      const aex = pos.x + Math.cos(aimAngle) * (r + aimLen);
      const aey = pos.y - Math.sin(aimAngle) * (r + aimLen);

      ctx.strokeStyle = 'rgba(220, 250, 80, 0.7)';
      ctx.lineWidth = 3;
      ctx.setLineDash([6, 4]);
      ctx.beginPath();
      ctx.moveTo(ax, ay);
      ctx.lineTo(aex, aey);
      ctx.stroke();
      ctx.setLineDash([]);

      const headLen = camera.toScreenDist(14);
      const headAngle = 0.42;
      ctx.fillStyle = 'rgba(220, 250, 80, 0.85)';
      ctx.beginPath();
      ctx.moveTo(aex, aey);
      ctx.lineTo(
        aex - Math.cos(aimAngle - headAngle) * headLen,
        aey + Math.sin(aimAngle - headAngle) * headLen
      );
      ctx.lineTo(
        aex - Math.cos(aimAngle + headAngle) * headLen,
        aey + Math.sin(aimAngle + headAngle) * headLen
      );
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle = 'rgba(60,80,10,0.9)';
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    if (isLocal) {
      const youFont = Math.max(10, camera.toScreenDist(16));
      ctx.font = `bold ${youFont}px sans-serif`;
      ctx.textAlign = 'center';
      ctx.fillStyle = 'rgba(0,0,0,0.7)';
      ctx.fillText('ВЫ', pos.x + 1, pos.y - r - camera.toScreenDist(15) + 1);
      ctx.fillStyle = COLORS.BALL;
      ctx.fillText('ВЫ', pos.x, pos.y - r - camera.toScreenDist(15));
    }

    const stamina = player.stamina != null ? player.stamina : MAX_STAMINA;
    const barW = camera.toScreenDist(44);
    const barH = camera.toScreenDist(7);
    const barX = pos.x - barW / 2;
    const barY = pos.y + r + camera.toScreenDist(8);

    ctx.fillStyle = 'rgba(0,0,0,0.7)';
    ctx.beginPath();
    if (ctx.roundRect) ctx.roundRect(barX - 1, barY - 1, barW + 2, barH + 2, 3);
    else ctx.rect(barX - 1, barY - 1, barW + 2, barH + 2);
    ctx.fill();

    const ratio = Math.max(0, Math.min(1, stamina / MAX_STAMINA));
    const sgrad = ctx.createLinearGradient(barX, barY, barX, barY + barH);
    if (ratio > 0.3) {
      sgrad.addColorStop(0, '#6ee39a');
      sgrad.addColorStop(1, '#1f8a4a');
    } else {
      sgrad.addColorStop(0, '#ff7f7f');
      sgrad.addColorStop(1, '#a81e1e');
    }
    ctx.fillStyle = sgrad;
    ctx.beginPath();
    if (ctx.roundRect) ctx.roundRect(barX, barY, barW * ratio, barH, 2);
    else ctx.rect(barX, barY, barW * ratio, barH);
    ctx.fill();

    ctx.strokeStyle = 'rgba(0,0,0,0.4)';
    ctx.lineWidth = 1;
    for (let i = 1; i < 4; i++) {
      const tx = barX + (barW * i) / 4;
      ctx.beginPath();
      ctx.moveTo(tx, barY);
      ctx.lineTo(tx, barY + barH);
      ctx.stroke();
    }
  }

  lighten(hex, amount) {
    
    if (!hex || hex[0] !== '#' || hex.length !== 7) return hex;
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    const lr = Math.min(255, Math.round(r + (255 - r) * amount));
    const lg = Math.min(255, Math.round(g + (255 - g) * amount));
    const lb = Math.min(255, Math.round(b + (255 - b) * amount));
    return `rgb(${lr}, ${lg}, ${lb})`;
  }
}
