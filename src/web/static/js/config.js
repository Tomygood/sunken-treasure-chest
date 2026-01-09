export const TILE_SIZE = 55;

export const ASSETS = {
  "void":    { type: "empty",    src: "./assets/tiles/void.png",     img: null, color: "lightgray" },
  "wall":    { type: "wall",     src: "./assets/tiles/void.png",     img: null, color: "#333" },
  "floor":   { type: "floor",    src: "./assets/tiles/floor.png",    img: null, color: "yellow" },
  "treasure":{ type: "treasure", src: "./assets/tiles/treasure.png",    img: null, color: "brown" },
  "entrance":{type: "entrance",  src: "./assets/tiles/entrance.png",       img: null, color: "brown"},

  "Paladin": { type: "paladin",  src: "./assets/entities/eel-01.png",     img: null, color: "blue" },
  "rat": { type: "rat",  src: "./assets/entities/fish-01.png",  img: null, color: "red" },

  "building":{ type: "building", src: "./assets/tiles/building.png", img: null, color: "green" },

  "wallB":    {type: "wall", src: "./assets/tiles/wallB.png",    img: null, color: "yellow"},
  "wallI":    {type: "wall", src: "./assets/tiles/wallI.png",    img: null, color: "yellow"},
  "wallT":    {type: "wall", src: "./assets/tiles/wallT.png",    img: null, color: "yellow"},
  "wallE":    {type: "wall", src: "./assets/tiles/wallE.png",    img: null, color: "yellow"},
  "wallBI":   {type: "wall", src: "./assets/tiles/wallBI.png",   img: null, color: "yellow"},
  "wallBT":   {type: "wall", src: "./assets/tiles/wallBT.png",   img: null, color: "yellow"},
  "wallBE":   {type: "wall", src: "./assets/tiles/wallBE.png",   img: null, color: "yellow"},
  "wallIT":   {type: "wall", src: "./assets/tiles/wallIT.png",   img: null, color: "yellow"},
  "wallIE":   {type: "wall", src: "./assets/tiles/wallIE.png",   img: null, color: "yellow"},
  "wallTE":   {type: "wall", src: "./assets/tiles/wallTE.png",   img: null, color: "yellow"},
  "wallBIT":  {type: "wall", src: "./assets/tiles/wallBIT.png",  img: null, color: "yellow"},
  "wallBIE":  {type: "wall", src: "./assets/tiles/wallBIE.png",  img: null, color: "yellow"},
  "wallBTE":  {type: "wall", src: "./assets/tiles/wallBTE.png",  img: null, color: "yellow"},
  "wallITE":  {type: "wall", src: "./assets/tiles/wallITE.png",  img: null, color: "yellow"},
  "wallBITE": {type: "wall", src: "./assets/tiles/wallBITE.png", img: null, color: "yellow"},

  "Explosive Trap": { type: "trap", src: "./assets/towers/explosive_trap.png", img: null, color: "orange" },
  "Pitfall": {type: "trap", src: "./assets/towers/pitfall.png", img: null, color: "lime"},
  "Archer Tower":  { type: "tower", src: "./assets/towers/archer_tower_1.png",    img: null, color: "purple" },
  "Archer Tower1":  { type: "tower", src: "./assets/towers/archer_tower_1.png",    img: null, color: "purple" },
  "Archer Tower2":  { type: "tower", src: "./assets/towers/archer_tower_2.png",    img: null, color: "purple" },
  "Archer Tower3":  { type: "tower", src: "./assets/towers/archer_tower_3.png",    img: null, color: "purple" },
  "Archer Tower4":  { type: "tower", src: "./assets/towers/archer_tower_4.png",    img: null, color: "purple" },
  "Archer Tower5":  { type: "tower", src: "./assets/towers/archer_tower_5.png",    img: null, color: "purple" },
  "Electric Tower": {type: "tower", src: "./assets/towers/electric_tower_1.png", img: null, color: "lime"},
  "Electric Tower1": {type: "tower", src: "./assets/towers/electric_tower_1.png", img: null, color: "lime"},
  "Electric Tower2": {type: "tower", src: "./assets/towers/electric_tower_2.png", img: null, color: "lime"},
  "Electric Tower3": {type: "tower", src: "./assets/towers/electric_tower_3.png", img: null, color: "lime"},
  "Placeable Wall" : {type: "tower", src: "./assets/towers/placed_wall_UD.png", img: null, color: "#333"},

  "Eel": { type: "Eel", src: "./assets/entities/eel-01.png", img: null, color: "blue"},
  "Clod": { type:"Clod", src: "./assets/entities/clod-01.png", img: null, color: "brown"},
  "Seal": {type: "Seal", src: "./assets/entities/seal-01.png", img: null, color: "lightblue"},
  "Fih": { type: "Fih", src: "./assets/entities/fish-01.png", img: null, color : "orange"},
  "Turtle": { type: "Turtle", src: "./assets/entities/turtle-01.png", img: null, color: "green"},

  "Liar1": { type: "Liar", src: "./assets/entities/boss1.png", img: null, color: "pink"},
  "Liar2": { type: "Liar", src: "./assets/entities/boss2.png", img: null, color: "pink"},

  "jewel": { type: "jewel", src: "./assets/gem2.png", img: null, color: "pink" },
  "title": { type: "title", src: "./assets/Title.png", img: null, color: "black" },
  "cutscene": { type: "cutscene", src: "./assets/cutscene.gif", img: null, color: "black" },
  "gameover": { type: "gameover", src: "./assets/gameover.gif", img: null, color: "black" },
  "credits": { type: "credits", src: "./assets/credits.png", img: null, color: "black" }
};

// Bestiary - Enemy descriptions and stats
export const BESTIARY = {
  "Eel": {
    name: "Eel",
    description: "Swift underwater creature. Fast but fragile.",
    stats: { hp: "Low", speed: "Fast", damage: "Medium" }
  },
  "Clod": {
    name: "Clod",
    description: "A fat and friendly underwater creature. Loves to eat, especially your towers :3",
    stats: { hp: "High", speed: "Slow", damage: "High" }
  },
  "Seal": {
    name: "Seal",
    description: "Playful marine friend. Balanced stats.",
    stats: { hp: "Medium", speed: "Medium", damage: "Medium" }
  },
  "Fih": {
    name: "Fih",
    description: "Cool fish with cool shoes. They are said to help them to run faster",
    stats: { hp: "Low", speed: "Fast", damage: "Low" }
  },
  "Turtle": {
    name: "Turtle",
    description: "Slow\n Slow\n Tanky",
    stats: { hp: "Very High", speed: "Very Slow", damage: "Low" }
  }
};

// Pre-load images logic
for (let key in ASSETS) {
  if (ASSETS[key].src) {
    ASSETS[key].img = new Image();
    ASSETS[key].img.src = ASSETS[key].src;
  }
}