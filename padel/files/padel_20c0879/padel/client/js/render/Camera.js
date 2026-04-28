import { COURT_WIDTH, COURT_LENGTH } from '../../../shared/constants.js';

export class Camera {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.margin = 60;
    this.scale = 1;
    this.offsetX = 0;
    this.offsetY = 0;
    this.resize();
  }

  resize() {
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = window.innerWidth * dpr;
    this.canvas.height = window.innerHeight * dpr;
    this.canvas.style.width = window.innerWidth + 'px';
    this.canvas.style.height = window.innerHeight + 'px';
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const availW = window.innerWidth - this.margin * 2;
    const availH = window.innerHeight - this.margin * 2;
    this.scale = Math.min(availW / COURT_WIDTH, availH / COURT_LENGTH);
    this.offsetX = (window.innerWidth - COURT_WIDTH * this.scale) / 2;
    this.offsetY = (window.innerHeight - COURT_LENGTH * this.scale) / 2;
  }

  toScreen(gameX, gameY) {
    return {
      x: this.offsetX + gameX * this.scale,
      y: this.offsetY + (COURT_LENGTH - gameY) * this.scale
    };
  }

  toScreenDist(dist) {
    return dist * this.scale;
  }

  clear() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }
}
