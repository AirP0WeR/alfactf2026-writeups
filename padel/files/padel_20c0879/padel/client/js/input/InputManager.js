export class InputManager {
  constructor() {
    this.keys = {};
    this.seq = 0;
    
    this.justPressedQueue = new Set();

    window.addEventListener('keydown', (e) => {
      if (!this.keys[e.code]) {
        
        this.justPressedQueue.add(e.code);
      }
      this.keys[e.code] = true;
      if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Space'].includes(e.code)) {
        e.preventDefault();
      }
    });

    window.addEventListener('keyup', (e) => {
      this.keys[e.code] = false;
    });

    window.addEventListener('blur', () => {
      this.keys = {};
      this.justPressedQueue.clear();
    });
  }

  wasJustPressed(code) {
    if (this.justPressedQueue.has(code)) {
      this.justPressedQueue.delete(code);
      return true;
    }
    return false;
  }

  clearFrame() {
    this.justPressedQueue.clear();
  }

  shotJustPressed() {
    return this.wasJustPressed('Space');
  }

  getInput() {
    const input = {
      seq: this.seq++,
      up: this.keys['KeyW'] || this.keys['ArrowUp'] || false,
      down: this.keys['KeyS'] || this.keys['ArrowDown'] || false,
      left: this.keys['KeyA'] || this.keys['ArrowLeft'] || false,
      right: this.keys['KeyD'] || this.keys['ArrowRight'] || false,
      sprint: this.keys['ShiftLeft'] || this.keys['ShiftRight'] || false,
      shot: this.keys['Space'] || false,
    };

    if (input.shot) {
      if (input.up) input.shotModifier = 'lob';
      else if (input.down) input.shotModifier = 'smash';
      else if (input.left) input.shotModifier = 'angle_left';
      else if (input.right) input.shotModifier = 'angle_right';
      else input.shotModifier = 'flat';
    }

    return input;
  }

  getMovementDir() {
    let dx = 0, dy = 0;
    if (this.keys['KeyA'] || this.keys['ArrowLeft']) dx -= 1;
    if (this.keys['KeyD'] || this.keys['ArrowRight']) dx += 1;
    if (this.keys['KeyW'] || this.keys['ArrowUp']) dy += 1;
    if (this.keys['KeyS'] || this.keys['ArrowDown']) dy -= 1;

    if (dx !== 0 && dy !== 0) {
      const inv = 1 / Math.SQRT2;
      dx *= inv;
      dy *= inv;
    }

    return { dx, dy };
  }

  isSprinting() {
    return this.keys['ShiftLeft'] || this.keys['ShiftRight'] || false;
  }

  isShotPressed() {
    return this.keys['Space'] || false;
  }
}
