import {
  COURT_LENGTH, COURT_WIDTH, NET_Y, SERVICE_LINE_DIST, CENTER_SERVICE_X,
  BACK_WALL_HEIGHT, BACK_WALL_GLASS_H, SIDE_WALL_GLASS_LENGTH,
  SIDE_WALL_GLASS_HEIGHT, FENCE_HEIGHT
} from './constants.js';

export const WALL_SEGMENTS = [
  
  { x1: 0, y1: 0, x2: COURT_WIDTH, y2: 0, height: BACK_WALL_HEIGHT, glassHeight: BACK_WALL_GLASS_H, type: 'back', normal: { x: 0, y: 1 } },
  
  { x1: 0, y1: COURT_LENGTH, x2: COURT_WIDTH, y2: COURT_LENGTH, height: BACK_WALL_HEIGHT, glassHeight: BACK_WALL_GLASS_H, type: 'back', normal: { x: 0, y: -1 } },
  
  { x1: 0, y1: 0, x2: 0, y2: COURT_LENGTH, height: FENCE_HEIGHT, glassHeight: SIDE_WALL_GLASS_HEIGHT, glassFromBack: SIDE_WALL_GLASS_LENGTH, type: 'side', normal: { x: 1, y: 0 } },
  
  { x1: COURT_WIDTH, y1: 0, x2: COURT_WIDTH, y2: COURT_LENGTH, height: FENCE_HEIGHT, glassHeight: SIDE_WALL_GLASS_HEIGHT, glassFromBack: SIDE_WALL_GLASS_LENGTH, type: 'side', normal: { x: -1, y: 0 } },
];

export const COURT_LINES = [
  
  { x1: 0, y1: 0, x2: COURT_WIDTH, y2: 0 },
  { x1: COURT_WIDTH, y1: 0, x2: COURT_WIDTH, y2: COURT_LENGTH },
  { x1: COURT_WIDTH, y1: COURT_LENGTH, x2: 0, y2: COURT_LENGTH },
  { x1: 0, y1: COURT_LENGTH, x2: 0, y2: 0 },
  
  { x1: 0, y1: NET_Y - SERVICE_LINE_DIST, x2: COURT_WIDTH, y2: NET_Y - SERVICE_LINE_DIST },
  { x1: 0, y1: NET_Y + SERVICE_LINE_DIST, x2: COURT_WIDTH, y2: NET_Y + SERVICE_LINE_DIST },
  
  { x1: CENTER_SERVICE_X, y1: NET_Y - SERVICE_LINE_DIST, x2: CENTER_SERVICE_X, y2: NET_Y },
  { x1: CENTER_SERVICE_X, y1: NET_Y, x2: CENTER_SERVICE_X, y2: NET_Y + SERVICE_LINE_DIST },
];

export const NET = {
  x1: 0,
  y1: NET_Y,
  x2: COURT_WIDTH,
  y2: NET_Y
};

export const SERVICE_BOXES = {
  
  team1: {
    deuce: { x1: CENTER_SERVICE_X, y1: NET_Y, x2: COURT_WIDTH, y2: NET_Y + SERVICE_LINE_DIST },
    ad: { x1: 0, y1: NET_Y, x2: CENTER_SERVICE_X, y2: NET_Y + SERVICE_LINE_DIST }
  },
  
  team2: {
    deuce: { x1: 0, y1: NET_Y - SERVICE_LINE_DIST, x2: CENTER_SERVICE_X, y2: NET_Y },
    ad: { x1: CENTER_SERVICE_X, y1: NET_Y - SERVICE_LINE_DIST, x2: COURT_WIDTH, y2: NET_Y }
  }
};

export const STARTING_POSITIONS = {
  team1: [
    { x: 300, y: 300 },
    { x: 700, y: 300 }
  ],
  team2: [
    { x: 300, y: 1700 },
    { x: 700, y: 1700 }
  ]
};
