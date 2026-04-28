import { COLORS } from '../../../shared/constants.js';

export class UIRenderer {
  constructor(camera) {
    this.camera = camera;
    this.ctx = camera.ctx;
  }

  drawScore(score) {
    if (!score) return;

    const { ctx } = this;
    const centerX = window.innerWidth / 2;
    const y = 15;

    const bgW = 350;
    const bgH = 50;
    ctx.fillStyle = COLORS.HUD_BG;
    ctx.beginPath();
    ctx.roundRect(centerX - bgW / 2, y, bgW, bgH, 8);
    ctx.fill();

    ctx.font = 'bold 16px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    const midY = y + bgH / 2;

    ctx.fillStyle = COLORS.TEAM1;
    ctx.fillText('Команда 1', centerX - 120, midY);

    ctx.fillStyle = '#fff';
    const pointLabels = ['0', '15', '30', '40', 'AD'];
    const t1p = score.advantage === 0 ? 4 : Math.min(score.points[0], 3);
    const t2p = score.advantage === 1 ? 4 : Math.min(score.points[1], 3);
    ctx.fillText(`${pointLabels[t1p]}`, centerX - 40, midY);

    ctx.font = '14px sans-serif';
    ctx.fillStyle = '#aaa';
    const g = score.games || [0, 0];
    ctx.fillText(`(${g[0]})`, centerX - 65, midY);

    ctx.fillStyle = '#555';
    ctx.font = 'bold 16px sans-serif';
    ctx.fillText('-', centerX, midY);

    ctx.fillStyle = COLORS.TEAM2;
    ctx.fillText('Команда 2', centerX + 120, midY);

    ctx.fillStyle = '#fff';
    ctx.fillText(`${pointLabels[t2p]}`, centerX + 40, midY);

    ctx.font = '14px sans-serif';
    ctx.fillStyle = '#aaa';
    ctx.fillText(`(${g[1]})`, centerX + 65, midY);

    if (score.sets && score.sets.length > 0) {
      ctx.font = '12px sans-serif';
      ctx.fillStyle = '#888';
      const setsStr = score.sets.map(s => `${s[0]}-${s[1]}`).join(' | ');
      ctx.fillText(setsStr, centerX, y + bgH + 15);
    }

    if (score.servingTeam != null) {
      const serveX = score.servingTeam === 0
        ? centerX - bgW / 2 - 14
        : centerX + bgW / 2 + 14;
      ctx.fillStyle = COLORS.BALL;
      ctx.beginPath();
      ctx.arc(serveX, midY, 5, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = 'rgba(0,0,0,0.6)';
      ctx.lineWidth = 1;
      ctx.stroke();
    }
  }

  drawMessage(text) {
    const { ctx } = this;
    ctx.fillStyle = 'rgba(0,0,0,0.6)';
    ctx.fillRect(0, 0, window.innerWidth, window.innerHeight);

    ctx.fillStyle = '#fff';
    ctx.font = 'bold 36px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, window.innerWidth / 2, window.innerHeight / 2);
  }

  drawServeInfo(serveInfo) {
    const { ctx } = this;
    const centerX = window.innerWidth / 2;
    const y = window.innerHeight - 80;

    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    if (serveInfo.state === 'waiting') {
      ctx.fillStyle = 'rgba(0,0,0,0.5)';
      ctx.beginPath();
      ctx.roundRect(centerX - 160, y - 20, 320, 50, 8);
      ctx.fill();

      ctx.fillStyle = '#c8e620';
      ctx.font = 'bold 18px sans-serif';
      if (serveInfo.isLocalServing) {
        ctx.fillText('Нажмите ПРОБЕЛ для подброса', centerX, y);
        if (serveInfo.faults > 0) {
          ctx.fillStyle = '#e63946';
          ctx.font = '14px sans-serif';
          ctx.fillText('Вторая подача', centerX, y + 18);
        }
      } else if (serveInfo.isTeammateServing) {
        ctx.fillText('Подаёт напарник...', centerX, y);
      } else {
        ctx.fillText('Подаёт соперник...', centerX, y);
      }
    } else if (serveInfo.state === 'tossed' && serveInfo.isLocalServing) {
      const tossTimer = serveInfo.tossTimer || 0;

      const power = Math.min(1.0, tossTimer / 0.6);
      const powerPct = Math.round(power * 100);

      const gaugeX = window.innerWidth - 70;
      const gaugeTop = window.innerHeight * 0.2;
      const gaugeH = window.innerHeight * 0.5;
      const gaugeW = 30;

      ctx.fillStyle = 'rgba(0,0,0,0.6)';
      ctx.beginPath();
      ctx.roundRect(gaugeX - gaugeW / 2 - 8, gaugeTop - 30, gaugeW + 16, gaugeH + 70, 10);
      ctx.fill();

      ctx.fillStyle = '#aaa';
      ctx.font = 'bold 12px sans-serif';
      ctx.fillText('СИЛА', gaugeX, gaugeTop - 14);

      ctx.fillStyle = 'rgba(255,255,255,0.1)';
      ctx.beginPath();
      ctx.roundRect(gaugeX - gaugeW / 2, gaugeTop, gaugeW, gaugeH, 4);
      ctx.fill();

      const zones = [
        { start: 0.00, end: 0.20, color: '#e74c3c' },
        { start: 0.20, end: 0.45, color: '#e67e22' },
        { start: 0.45, end: 0.75, color: '#f1c40f' },
        { start: 0.75, end: 1.00, color: '#2ecc71' },
      ];
      for (const z of zones) {
        ctx.fillStyle = z.color + '99';
        const zy = gaugeTop + (1 - z.end) * gaugeH;
        const zh = (z.end - z.start) * gaugeH;
        ctx.fillRect(gaugeX - gaugeW / 2, zy, gaugeW, zh);
      }

      ctx.strokeStyle = '#2ecc71';
      ctx.lineWidth = 2;
      ctx.strokeRect(gaugeX - gaugeW / 2, gaugeTop, gaugeW, 0.25 * gaugeH);

      const indicatorY = gaugeTop + (1 - power) * gaugeH;
      const bottomY = gaugeTop + gaugeH;

      let currentColor = '#e74c3c';
      for (const z of zones) {
        if (power >= z.start && power <= z.end) { currentColor = z.color; break; }
      }

      ctx.fillStyle = currentColor + 'DD';
      ctx.fillRect(gaugeX - gaugeW / 2, indicatorY, gaugeW, bottomY - indicatorY);

      const glow = ctx.createRadialGradient(gaugeX, indicatorY, 0, gaugeX, indicatorY, 30);
      glow.addColorStop(0, currentColor + '80');
      glow.addColorStop(1, 'transparent');
      ctx.fillStyle = glow;
      ctx.fillRect(gaugeX - 30, indicatorY - 30, 60, 60);

      ctx.fillStyle = '#fff';
      ctx.beginPath();
      ctx.moveTo(gaugeX - gaugeW / 2 - 10, indicatorY);
      ctx.lineTo(gaugeX - gaugeW / 2 - 2, indicatorY - 6);
      ctx.lineTo(gaugeX - gaugeW / 2 - 2, indicatorY + 6);
      ctx.fill();

      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(gaugeX - gaugeW / 2, indicatorY);
      ctx.lineTo(gaugeX + gaugeW / 2, indicatorY);
      ctx.stroke();

      ctx.fillStyle = currentColor;
      ctx.font = 'bold 22px sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText(`${powerPct}%`, gaugeX - gaugeW / 2 - 16, indicatorY + 1);
      ctx.textAlign = 'center';

      ctx.fillStyle = 'rgba(0,0,0,0.5)';
      ctx.beginPath();
      ctx.roundRect(centerX - 140, y - 18, 280, 40, 8);
      ctx.fill();

      if (power >= 0.95) {
        ctx.fillStyle = '#2ecc71';
        ctx.font = 'bold 22px sans-serif';
        ctx.fillText('ЖМИ ПРОБЕЛ!', centerX, y);
      } else if (power >= 0.75) {
        ctx.fillStyle = '#f1c40f';
        ctx.font = 'bold 18px sans-serif';
        ctx.fillText('Почти... ПРОБЕЛ для удара', centerX, y);
      } else {
        ctx.fillStyle = '#fff';
        ctx.font = '16px sans-serif';
        ctx.fillText('Держите… сила накапливается', centerX, y);
      }
    }
  }

  drawServeTiming(timingInfo) {
    if (!timingInfo) return;
    const { ctx } = this;
    const centerX = window.innerWidth / 2;
    const y = window.innerHeight / 2 - 60;

    const alpha = Math.min(1, timingInfo.timer * 2);
    const colors = {
      perfect: '#2ecc71',
      good: '#f1c40f',
      early: '#e67e22',
      late: '#e74c3c'
    };
    const labels = {
      perfect: 'PERFECT SERVE!',
      good: 'GOOD SERVE',
      early: 'TOO EARLY',
      late: 'TOO LATE'
    };

    const color = colors[timingInfo.rating] || '#fff';
    const label = labels[timingInfo.rating] || '';

    const floatY = y - (1 - alpha) * 30;

    ctx.globalAlpha = alpha;

    ctx.fillStyle = 'rgba(0,0,0,0.5)';
    ctx.beginPath();
    ctx.roundRect(centerX - 120, floatY - 22, 240, 44, 10);
    ctx.fill();

    ctx.fillStyle = color;
    ctx.font = 'bold 26px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, centerX, floatY);

    ctx.globalAlpha = 1;
  }

  drawSwingTimingBar(swingInfo) {
    if (!swingInfo) return;
    const { ctx } = this;
    const { progress, sweetStart, sweetEnd, power, connected } = swingInfo;

    const barW = 240;
    const barH = 16;
    const x = window.innerWidth / 2 - barW / 2;
    const y = window.innerHeight - 130;

    ctx.fillStyle = 'rgba(0,0,0,0.55)';
    ctx.beginPath();
    ctx.roundRect(x - 12, y - 26, barW + 24, barH + 42, 8);
    ctx.fill();

    ctx.fillStyle = '#aaa';
    ctx.font = 'bold 11px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'alphabetic';
    ctx.fillText(connected ? 'CONTACT' : 'SWING — TIME YOUR HIT', x + barW / 2, y - 10);

    ctx.fillStyle = 'rgba(255,255,255,0.12)';
    ctx.beginPath();
    ctx.roundRect(x, y, barW, barH, 4);
    ctx.fill();

    ctx.fillStyle = '#e67e2299';
    ctx.fillRect(x, y, barW * sweetStart, barH);

    const sweetX = x + barW * sweetStart;
    const sweetW = barW * (sweetEnd - sweetStart);
    ctx.fillStyle = '#2ecc7166';
    ctx.fillRect(sweetX, y, sweetW, barH);
    ctx.strokeStyle = '#2ecc71';
    ctx.lineWidth = 2;
    ctx.strokeRect(sweetX, y, sweetW, barH);

    const followX = x + barW * sweetEnd;
    const followW = barW * (1 - sweetEnd);
    ctx.fillStyle = '#e67e2299';
    ctx.fillRect(followX, y, followW, barH);

    const headX = x + barW * progress;
    ctx.strokeStyle = connected ? '#2ecc71' : '#fff';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(headX, y - 4);
    ctx.lineTo(headX, y + barH + 4);
    ctx.stroke();

    let labelColor = '#e74c3c';
    if (power >= 0.95) labelColor = '#2ecc71';
    else if (power >= 0.8) labelColor = '#f1c40f';
    else if (power >= 0.65) labelColor = '#e67e22';

    ctx.fillStyle = labelColor;
    ctx.font = 'bold 12px sans-serif';
    ctx.textBaseline = 'top';
    ctx.fillText(`${Math.round(power * 100)}%`, x + barW / 2, y + barH + 4);
    ctx.textBaseline = 'alphabetic';
  }

  drawDebugInfo(info) {
    const { ctx } = this;
    ctx.fillStyle = '#666';
    ctx.font = '12px monospace';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';

    const lines = Object.entries(info);
    lines.forEach(([key, val], i) => {
      ctx.fillText(`${key}: ${val}`, 10, 10 + i * 16);
    });
  }
}
