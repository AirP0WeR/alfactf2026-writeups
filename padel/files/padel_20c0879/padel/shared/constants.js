
export const COURT_LENGTH = 2000;
export const COURT_WIDTH = 1000;
export const NET_Y = 1000;
export const NET_HEIGHT = 88;
export const NET_POST_HEIGHT = 92;
export const SERVICE_LINE_DIST = 695;
export const CENTER_SERVICE_X = 500;

export const BACK_WALL_HEIGHT = 400;
export const BACK_WALL_GLASS_H = 300;
export const SIDE_WALL_GLASS_LENGTH = 400;
export const SIDE_WALL_GLASS_HEIGHT = 300;
export const FENCE_HEIGHT = 400;
export const FENCE_HEIGHT_CENTER = 300;

export const GRAVITY = 980;
export const BALL_RADIUS = 3.63;
export const BALL_BOUNCE_COEFF = 0.62;
export const WALL_BOUNCE_COEFF = 0.65;
export const BALL_DRAG = 0.005;
export const SPIN_FACTOR = 0.22;
export const MAX_BALL_SPEED = 3600;

export const PLAYER_RADIUS = 20;
export const PLAYER_MAX_SPEED = 500;
export const PLAYER_SPRINT_SPEED = 750;
export const PLAYER_ACCELERATION = 2000;
export const PLAYER_DECELERATION = 3000;
export const SHOT_REACH = 150;
export const PADDLE_LENGTH = 40;
export const MAX_STAMINA = 33;
export const STAMINA_DRAIN = 20;
export const STAMINA_REGEN = 15;

export const SWING_WINDUP = 150;
export const SWING_SWEET_SPOT = 100;
export const SWING_FOLLOW_THROUGH = 200;
export const SWING_TOTAL = SWING_WINDUP + SWING_SWEET_SPOT + SWING_FOLLOW_THROUGH;

export const SHOT_TYPES = {
  FLAT: 'flat',
  LOB: 'lob',
  SMASH: 'smash',
  SLICE: 'slice',
  VOLLEY: 'volley',
  ANGLED: 'angled'
};

export const SHOT_PARAMS = {
  flat:   { speed: 1100, vz: 260, spin: 0.1 },
  lob:    { speed: 650,  vz: 1100, spin: -0.4 },
  smash:  { speed: 2400, vz: -100, spin: 0.5 },
  slice:  { speed: 850,  vz: 170, spin: -0.6 },
  volley: { speed: 1050, vz: 120, spin: 0.05 },
  angled: { speed: 950,  vz: 220, spin: 0.3 }
};

export const SERVER_TICK_RATE = 60;
export const CLIENT_RENDER_RATE = 60;
export const INTERPOLATION_DELAY = 100;

export const GAME_STATES = {
  WAITING: 'waiting',
  READY_CHECK: 'ready_check',
  SERVING: 'serving',
  PLAYING: 'playing',
  POINT_SCORED: 'point_scored',
  SET_ENDED: 'set_ended',
  MATCH_ENDED: 'match_ended'
};

export const PLAYER_STATES = {
  IDLE: 'idle',
  MOVING: 'moving',
  SWINGING: 'swinging',
  SERVING: 'serving',
  RECOVERING: 'recovering'
};

export const BALL_STATES = {
  IN_PLAY: 'in_play',
  DEAD: 'dead',
  SERVING: 'serving'
};

export const COLORS = {
  COURT: '#2171b5',
  COURT_LINES: '#ffffff',
  WALL_GLASS: 'rgba(200, 230, 255, 0.6)',
  WALL_FENCE: '#888888',
  NET: '#333333',
  BALL: '#c8e620',
  BALL_SHADOW: 'rgba(0, 0, 0, 0.3)',
  TEAM1: '#e63946',
  TEAM2: '#457b9d',
  PLAYER_OUTLINE: '#1d3557',
  STAMINA_BG: '#333333',
  STAMINA_FILL: '#2ecc71',
  HUD_BG: 'rgba(0, 0, 0, 0.7)',
  HUD_TEXT: '#ffffff'
};
