import { COURT_WIDTH, COURT_LENGTH, NET_Y, COLORS, SERVICE_LINE_DIST, CENTER_SERVICE_X } from '../../../shared/constants.js';
import { COURT_LINES, NET, WALL_SEGMENTS } from '../../../shared/CourtLayout.js';

export class CourtRenderer {
  constructor(camera) {
    this.camera = camera;
    this.ctx = camera.ctx;
  }

  draw() {
    this.drawOuterShadow();
    this.drawSurface();
    this.drawLines();
    this.drawWalls();
    this.drawNet();
  }

  drawOuterShadow() {
    const { ctx, camera } = this;
    const tl = camera.toScreen(0, COURT_LENGTH);
    const w = camera.toScreenDist(COURT_WIDTH);
    const h = camera.toScreenDist(COURT_LENGTH);
    const pad = camera.toScreenDist(60);

    ctx.save();
    ctx.shadowColor = 'rgba(0,0,0,0.55)';
    ctx.shadowBlur = pad;
    ctx.shadowOffsetY = camera.toScreenDist(12);
    ctx.fillStyle = '#000';
    ctx.fillRect(tl.x, tl.y, w, h);
    ctx.restore();
  }

  drawSurface() {
    const { ctx, camera } = this;
    const tl = camera.toScreen(0, COURT_LENGTH);
    const w = camera.toScreenDist(COURT_WIDTH);
    const h = camera.toScreenDist(COURT_LENGTH);

    const grad = ctx.createLinearGradient(tl.x, tl.y, tl.x, tl.y + h);
    grad.addColorStop(0, '#1e6aa8');
    grad.addColorStop(0.5, '#2b82c9');
    grad.addColorStop(1, '#1e6aa8');
    ctx.fillStyle = grad;
    ctx.fillRect(tl.x, tl.y, w, h);

    const boxGrad = ctx.createLinearGradient(0, tl.y, 0, tl.y + h);
    boxGrad.addColorStop(0, 'rgba(255,255,255,0.08)');
    boxGrad.addColorStop(0.5, 'rgba(255,255,255,0.02)');
    boxGrad.addColorStop(1, 'rgba(255,255,255,0.08)');
    ctx.fillStyle = boxGrad;
    const boxTop = camera.toScreen(0, NET_Y + SERVICE_LINE_DIST);
    const boxBot = camera.toScreen(COURT_WIDTH, NET_Y - SERVICE_LINE_DIST);
    ctx.fillRect(boxTop.x, boxTop.y, boxBot.x - boxTop.x, boxBot.y - boxTop.y);

    ctx.save();
    ctx.beginPath();
    ctx.rect(tl.x, tl.y, w, h);
    ctx.clip();
    ctx.strokeStyle = 'rgba(255,255,255,0.035)';
    ctx.lineWidth = 1;
    const stripeSpacing = Math.max(3, camera.toScreenDist(8));
    for (let sx = tl.x; sx < tl.x + w; sx += stripeSpacing) {
      ctx.beginPath();
      ctx.moveTo(sx, tl.y);
      ctx.lineTo(sx, tl.y + h);
      ctx.stroke();
    }
    ctx.restore();

    const netScreen = camera.toScreen(0, NET_Y).y;
    const netGrad = ctx.createLinearGradient(0, netScreen - 40, 0, netScreen + 40);
    netGrad.addColorStop(0, 'rgba(0,0,0,0)');
    netGrad.addColorStop(0.5, 'rgba(0,0,0,0.18)');
    netGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = netGrad;
    ctx.fillRect(tl.x, netScreen - 40, w, 80);
  }

  drawLines() {
    const { ctx, camera } = this;
    ctx.setLineDash([]);
    ctx.lineCap = 'square';
    const lineW = Math.max(2, camera.toScreenDist(5));

    for (const line of COURT_LINES) {
      const from = camera.toScreen(line.x1, line.y1);
      const to = camera.toScreen(line.x2, line.y2);

      ctx.strokeStyle = 'rgba(0,0,0,0.35)';
      ctx.lineWidth = lineW;
      ctx.beginPath();
      ctx.moveTo(from.x, from.y + 2);
      ctx.lineTo(to.x, to.y + 2);
      ctx.stroke();

      ctx.strokeStyle = COLORS.COURT_LINES;
      ctx.lineWidth = lineW;
      ctx.beginPath();
      ctx.moveTo(from.x, from.y);
      ctx.lineTo(to.x, to.y);
      ctx.stroke();

      ctx.strokeStyle = 'rgba(255,255,255,0.35)';
      ctx.lineWidth = Math.max(1, lineW * 0.35);
      ctx.beginPath();
      ctx.moveTo(from.x, from.y - 1);
      ctx.lineTo(to.x, to.y - 1);
      ctx.stroke();
    }
  }

  drawNet() {
    const { ctx, camera } = this;
    const from = camera.toScreen(NET.x1, NET.y1);
    const to = camera.toScreen(NET.x2, NET.y2);

    ctx.strokeStyle = 'rgba(0,0,0,0.35)';
    ctx.lineWidth = Math.max(4, camera.toScreenDist(14));
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(from.x, from.y + 3);
    ctx.lineTo(to.x, to.y + 3);
    ctx.stroke();

    const bandH = Math.max(6, camera.toScreenDist(18));
    const bandY = from.y - bandH / 2;
    const bandX = from.x;
    const bandW = to.x - from.x;

    ctx.fillStyle = '#2a2a2a';
    ctx.fillRect(bandX, bandY, bandW, bandH);

    ctx.save();
    ctx.beginPath();
    ctx.rect(bandX, bandY, bandW, bandH);
    ctx.clip();
    ctx.strokeStyle = 'rgba(180,180,180,0.55)';
    ctx.lineWidth = 1;
    const step = Math.max(3, camera.toScreenDist(6));
    for (let i = -bandH; i < bandW + bandH; i += step) {
      ctx.beginPath();
      ctx.moveTo(bandX + i, bandY);
      ctx.lineTo(bandX + i + bandH, bandY + bandH);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(bandX + i, bandY + bandH);
      ctx.lineTo(bandX + i + bandH, bandY);
      ctx.stroke();
    }
    ctx.restore();

    ctx.fillStyle = '#f5f5f5';
    ctx.fillRect(bandX, bandY - Math.max(1, camera.toScreenDist(2)), bandW, Math.max(2, camera.toScreenDist(3)));
    ctx.fillStyle = '#111';
    ctx.fillRect(bandX, bandY + bandH, bandW, Math.max(1, camera.toScreenDist(2)));

    const postW = Math.max(6, camera.toScreenDist(16));
    const postH = Math.max(10, camera.toScreenDist(26));
    const posts = [from, to];
    for (const p of posts) {
      const px = p.x - postW / 2;
      const py = p.y - postH / 2;
      const pg = ctx.createLinearGradient(px, 0, px + postW, 0);
      pg.addColorStop(0, '#333');
      pg.addColorStop(0.5, '#888');
      pg.addColorStop(1, '#333');
      ctx.fillStyle = pg;
      ctx.fillRect(px, py, postW, postH);
      ctx.strokeStyle = '#111';
      ctx.lineWidth = 1;
      ctx.strokeRect(px, py, postW, postH);
    }
  }

  drawWalls() {
    const { ctx, camera } = this;
    const wallThickness = camera.toScreenDist(30);

    for (const seg of WALL_SEGMENTS) {
      const from = camera.toScreen(seg.x1, seg.y1);
      const to = camera.toScreen(seg.x2, seg.y2);
      const isHorizontal = seg.y1 === seg.y2;

      let rectX, rectY, rectW, rectH;
      if (isHorizontal) {
        const yOffset = seg.normal.y > 0 ? -wallThickness : 0;
        rectX = from.x;
        rectY = from.y + yOffset;
        rectW = to.x - from.x;
        rectH = wallThickness;
      } else {
        const xOffset = seg.normal.x > 0 ? -wallThickness : 0;
        rectX = from.x + xOffset;
        rectY = Math.min(from.y, to.y);
        rectW = wallThickness;
        rectH = Math.abs(to.y - from.y);
      }

      const grad = isHorizontal
        ? ctx.createLinearGradient(0, rectY, 0, rectY + rectH)
        : ctx.createLinearGradient(rectX, 0, rectX + rectW, 0);
      grad.addColorStop(0, 'rgba(180, 220, 255, 0.55)');
      grad.addColorStop(0.5, 'rgba(80, 140, 200, 0.25)');
      grad.addColorStop(1, 'rgba(180, 220, 255, 0.55)');
      ctx.fillStyle = grad;
      ctx.fillRect(rectX, rectY, rectW, rectH);

      ctx.strokeStyle = 'rgba(220, 240, 255, 0.75)';
      ctx.lineWidth = 2;
      ctx.strokeRect(rectX, rectY, rectW, rectH);

      ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
      ctx.lineWidth = 1;
      if (isHorizontal) {
        ctx.beginPath();
        ctx.moveTo(rectX + 4, rectY + 3);
        ctx.lineTo(rectX + rectW - 4, rectY + 3);
        ctx.stroke();
      } else {
        ctx.beginPath();
        ctx.moveTo(rectX + 3, rectY + 4);
        ctx.lineTo(rectX + 3, rectY + rectH - 4);
        ctx.stroke();
      }

      ctx.strokeStyle = 'rgba(30, 60, 90, 0.45)';
      ctx.lineWidth = 1;
      const panelSpacing = Math.max(20, camera.toScreenDist(200));
      if (isHorizontal) {
        for (let x = rectX + panelSpacing; x < rectX + rectW; x += panelSpacing) {
          ctx.beginPath();
          ctx.moveTo(x, rectY);
          ctx.lineTo(x, rectY + rectH);
          ctx.stroke();
        }
      } else {
        for (let y = rectY + panelSpacing; y < rectY + rectH; y += panelSpacing) {
          ctx.beginPath();
          ctx.moveTo(rectX, y);
          ctx.lineTo(rectX + rectW, y);
          ctx.stroke();
        }
      }
    }
  }

  drawServeBox(serveInfo) {
    const { ctx, camera } = this;

    let x1, y1, x2, y2;
    if (serveInfo.servingTeam === 0) {
      y1 = NET_Y;
      y2 = NET_Y + SERVICE_LINE_DIST;
      if (serveInfo.serveSide === 'deuce') {
        x1 = 0; x2 = CENTER_SERVICE_X;
      } else {
        x1 = CENTER_SERVICE_X; x2 = COURT_WIDTH;
      }
    } else {
      y1 = NET_Y - SERVICE_LINE_DIST;
      y2 = NET_Y;
      if (serveInfo.serveSide === 'deuce') {
        x1 = CENTER_SERVICE_X; x2 = COURT_WIDTH;
      } else {
        x1 = 0; x2 = CENTER_SERVICE_X;
      }
    }

    const tl = camera.toScreen(x1, y2);
    const br = camera.toScreen(x2, y1);
    const w = br.x - tl.x;
    const h = br.y - tl.y;

    const pulse = 0.3 + Math.sin(Date.now() / 300) * 0.15;
    const cx = tl.x + w / 2;
    const cy = tl.y + h / 2;
    const glow = ctx.createRadialGradient(cx, cy, 0, cx, cy, Math.max(w, h) * 0.7);
    glow.addColorStop(0, `rgba(200, 230, 32, ${pulse + 0.15})`);
    glow.addColorStop(1, `rgba(200, 230, 32, 0)`);
    ctx.fillStyle = glow;
    ctx.fillRect(tl.x, tl.y, w, h);

    ctx.fillStyle = `rgba(200, 230, 32, ${pulse * 0.6})`;
    ctx.fillRect(tl.x, tl.y, w, h);

    ctx.strokeStyle = `rgba(220, 250, 80, 0.9)`;
    ctx.lineWidth = 3;
    ctx.setLineDash([8, 4]);
    ctx.strokeRect(tl.x, tl.y, w, h);
    ctx.setLineDash([]);
  }
}
