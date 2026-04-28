import { Camera } from './Camera.js';
import { CourtRenderer } from './CourtRenderer.js';
import { PlayerRenderer } from './PlayerRenderer.js';
import { BallRenderer } from './BallRenderer.js';
import { UIRenderer } from './UIRenderer.js';

export class Renderer {
  constructor(canvas) {
    this.camera = new Camera(canvas);
    this.court = new CourtRenderer(this.camera);
    this.player = new PlayerRenderer(this.camera);
    this.ball = new BallRenderer(this.camera);
    this.ui = new UIRenderer(this.camera);

    window.addEventListener('resize', () => this.camera.resize());
  }

  render(gameState) {
    this.camera.clear();

    this.court.draw();

    if (gameState.serveInfo) {
      this.court.drawServeBox(gameState.serveInfo);
    }

    if (gameState.players) {
      for (const p of gameState.players) {
        this.player.draw(p, p.id === gameState.localPlayerId);
      }
    }

    if (gameState.ball) {
      this.ball.draw(gameState.ball);
    }

    if (gameState.score) {
      this.ui.drawScore(gameState.score);
    }

    if (gameState.serveInfo) {
      this.ui.drawServeInfo(gameState.serveInfo);
    }

    if (gameState.message) {
      this.ui.drawMessage(gameState.message);
    }
  }
}
