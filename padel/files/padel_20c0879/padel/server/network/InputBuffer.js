export class InputBuffer {
  constructor() {
    this.buffers = new Map();
    this.lastProcessedSeq = new Map();
  }

  addPlayer(playerId) {
    this.buffers.set(playerId, []);
    this.lastProcessedSeq.set(playerId, -1);
  }

  removePlayer(playerId) {
    this.buffers.delete(playerId);
    this.lastProcessedSeq.delete(playerId);
  }

  pushInput(playerId, input) {
    const buffer = this.buffers.get(playerId);
    if (!buffer) return;

    if (buffer.length > 30) {
      buffer.shift();
    }

    buffer.push(input);
  }

  getInputs(playerId) {
    const buffer = this.buffers.get(playerId);
    if (!buffer || buffer.length === 0) return null;

    const inputs = [...buffer];
    buffer.length = 0;

    if (inputs.length > 0) {
      this.lastProcessedSeq.set(playerId, inputs[inputs.length - 1].seq);
    }

    return inputs;
  }

  getLastProcessedSeq(playerId) {
    return this.lastProcessedSeq.get(playerId) || -1;
  }
}
