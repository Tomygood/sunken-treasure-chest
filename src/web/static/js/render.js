import { TILE_SIZE, ASSETS, BESTIARY } from './config.js';
import { placeable_buildings, state, inMenu, onTitleScreen, inCutscene, loadSplashTexts, currentSplashText, splashFlashOpacity, updateSplashFlash, selectRandomSplashText } from './state.js';
import { transform_mat } from './transform_mat.js';
import { completeCutsceneAndStartGame } from './network.js';
import { playSound } from './sound.js';
import { save_state, load_state } from './save.js';

let canvas;
let ctx;

const FONT_NAME = '"Press Start 2P", "Courier New", monospace'; 
const FONT_URL = 'https://fonts.gstatic.com/s/pressstart2p/v15/e3t4euO8T-267oIAQAu6jDQyK3nVivM.woff2';

let MAP_LIST = [];
const TILE_PREVIEW_COLORS = {
    void: "#2c3e50",
    wall: "#7f8c8d",
    floor: "#95a5a6",
    building: "#3498db",
    treasure: "#f1c40f",
    entrance: "#e74c3c"
};

export function getMenuCards() {
    return MAP_LIST;
}

let hoveredStaticButtonId = null;
export function setHoveredStaticButton(id) {
    hoveredStaticButtonId = id;
}

export const MENU_CONFIG = {
    width: 800,
    height: 600,
    buttons: [
        { label: "Level 1", id: 1, x: 300, y: 200, w: 200, h: 50 },
        { label: "Level 2", id: 2, x: 300, y: 300, w: 200, h: 50 },
        { label: "Level 3", id: 3, x: 300, y: 400, w: 200, h: 50 }
    ]
};

function pixel(x) { return x * TILE_SIZE; }

// --- NEW HELPER FOR PIXEL ART BUTTONS ---
function drawPixelButton(ctx, x, y, w, h, isHover, text, subText = null) {
    // Colors
    const baseColor = isHover ? "#3498db" : "#2980b9"; // Light blue / Darker blue
    const highlight = isHover ? "#5dade2" : "#5dade2"; // Top/Left highlight
    const shadow    = isHover ? "#1f618d" : "#1a5276"; // Bottom/Right shadow
    const textColor = "#ffffff";

    // 1. Main Body
    ctx.fillStyle = baseColor;
    ctx.fillRect(x + 4, y + 4, w - 8, h - 8);

    // 2. Borders
    const b = 4;

    // Top Edge (Highlight)
    ctx.fillStyle = highlight;
    ctx.fillRect(x, y, w, b); 
    // Left Edge (Highlight)
    ctx.fillRect(x, y, b, h);

    // Bottom Edge (Shadow)
    ctx.fillStyle = shadow;
    ctx.fillRect(x, y + h - b, w, b);
    // Right Edge (Shadow)
    ctx.fillRect(x + w - b, y, b, h);

    // 3. Text
    ctx.textAlign = "center";
    ctx.fillStyle = textColor;
    
    if (subText) {
        // Title
        ctx.font = `12px ${FONT_NAME}`;
        ctx.fillText(text, x + w / 2, y + 30);
        // Subtitle
        ctx.fillStyle = "#bdc3c7"; // Greyer text for details
        ctx.font = `8px ${FONT_NAME}`;
        ctx.fillText(subText, x + w / 2, y + 50);
    } else {
        // Centered single text
        ctx.font = `14px ${FONT_NAME}`;
        ctx.fillText(text, x + w / 2, y + h / 2 + 5);
    }
}

export function loadAssets() {
    const promises = [];
    for (const key in ASSETS) {
        const asset = ASSETS[key];
        if (asset.src) {
            const p = new Promise((resolve) => {
                const img = new Image();
                img.src = asset.src;
                img.onload = () => { asset.img = img; resolve(); };
                img.onerror = () => { console.error(`Failed: ${asset.src}`); asset.img = null; resolve(); };
            });
            promises.push(p);
        }
    }

    // Load custom font using CSS
    const fontPromise = (async () => {
        try {
            // Create a style element to inject @font-face
            const style = document.createElement('style');
            style.textContent = `
                @font-face {
                    font-family: 'Press Start 2P';
                    src: url('${FONT_URL}') format('woff2');
                    font-weight: normal;
                    font-style: normal;
                }
            `;
            document.head.appendChild(style);
            
            // Wait for font to be ready
            await document.fonts.load('12px "Press Start 2P"');
            console.log("Press Start 2P font loaded successfully");
        } catch (err) {
            console.error("Failed to load font:", err);
            console.log("Falling back to system fonts");
        }
    })();
    
    promises.push(fontPromise);

    return Promise.all(promises);
}

export async function loadMapList() {
    try {
        const resp = await fetch('/list-maps');
        if (!resp.ok) throw new Error('Failed to load map list');
        MAP_LIST = await resp.json();
    } catch (err) {
        console.error('Error loading map list', err);
        MAP_LIST = [];
    }
}

function draw_asset(asset, gridX, gridY) {
    if (!asset) return;
    const px = pixel(gridX);
    const py = pixel(gridY);
    const isImageValid = asset.img && asset.img.complete && asset.img.naturalWidth > 0;


    if (isImageValid) {
        ctx.drawImage(asset.img, px, py, TILE_SIZE, TILE_SIZE);
    } else {
        console.warn(`Asset image missing or failed to load for key: ${asset.src}`);
        ctx.fillStyle = asset.color || "magenta";
        ctx.fillRect(px, py, TILE_SIZE, TILE_SIZE);
    }
}

function draw_entities(list) {
    if (!list) return;
    list.forEach(entity => {
        var asset = "";
        if (entity.name == "Archer Tower" || entity.name == "Electric Tower") {
            asset = ASSETS[entity.name + entity.level];
        } else if (entity.name == "Liar"){
            if (entity.speed == 2) {
                asset = ASSETS["Liar2"]
            } else {
                asset = ASSETS["Liar1"]
            }
        } else {
            asset = ASSETS[entity?.name] || (entity && Object.prototype.hasOwnProperty.call(entity, 'level') ? ASSETS['building'] : null);
        }
        if (!asset) return;

        draw_asset(asset, entity.position[1], entity.position[0]);

        if (entity.hp !== undefined && entity.maxhp !== undefined) {
            const hpPercent = Math.max(0, Math.min(1, entity.hp / entity.maxhp));
            draw_hp_bar(
                pixel(entity.position[1]) + 2, 
                pixel(entity.position[0]) + TILE_SIZE, 
                TILE_SIZE - 4, 6, hpPercent
            );
        }
    });
}

function draw_hp_bar(x, y, width, height, percent) {
    const filledWidth = Math.max(0, Math.min(width, width * percent));
    ctx.fillStyle = '#c0392b'; // Darker red background
    ctx.fillRect(x, y, width, height);
    ctx.fillStyle = '#2ecc71'; // Pixel green
    ctx.fillRect(x, y, filledWidth, height);
    // Add a pixel border to the HP bar too
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 2;
    ctx.strokeRect(x, y, width, height);
}

function drawBestiary() {
    let bestiaryPanel = document.getElementById("bestiary-panel");
    if (!bestiaryPanel) {
        bestiaryPanel = document.createElement("div");
        bestiaryPanel.id = "bestiary-panel";
        bestiaryPanel.style.position = "fixed";
        bestiaryPanel.style.right = "20px";
        bestiaryPanel.style.top = "140px";
        bestiaryPanel.style.width = "380px";
        bestiaryPanel.style.maxHeight = "calc(100vh - 160px)";
        bestiaryPanel.style.overflowY = "auto";
        bestiaryPanel.style.background = "#34495e";
        bestiaryPanel.style.border = "4px solid #f1c40f";
        bestiaryPanel.style.borderRadius = "8px";
        bestiaryPanel.style.boxShadow = "0 8px 0 #1a252f";
        bestiaryPanel.style.padding = "20px";
        bestiaryPanel.style.zIndex = "100";
        bestiaryPanel.style.fontFamily = FONT_NAME;
        
        // Title
        const title = document.createElement("div");
        title.style.fontSize = "20px";
        title.style.color = "#f1c40f";
        title.style.textAlign = "center";
        title.style.marginBottom = "20px";
        title.style.fontWeight = "bold";
        title.innerText = "BESTIARY";
        bestiaryPanel.appendChild(title);
        
        // Add enemy entries
        const enemies = Object.values(BESTIARY).filter(e => e.name !== "Liar");
        enemies.forEach((enemy, idx) => {
            const entry = document.createElement("div");
            entry.style.background = "#2c3e50";
            entry.style.border = "2px solid #7f8c8d";
            entry.style.borderRadius = "6px";
            entry.style.padding = "12px";
            entry.style.marginBottom = "12px";
            entry.style.display = "flex";
            entry.style.gap = "12px";
            
            // Enemy sprite
            const asset = ASSETS[enemy.name];
            if (asset && asset.img) {
                const sprite = document.createElement("img");
                sprite.src = asset.src;
                sprite.style.width = "60px";
                sprite.style.height = "60px";
                sprite.style.imageRendering = "pixelated";
                sprite.style.flexShrink = "0";
                entry.appendChild(sprite);
            }
            
            // Info container
            const info = document.createElement("div");
            info.style.flex = "1";
            
            // Name
            const name = document.createElement("div");
            name.style.fontSize = "14px";
            name.style.color = "#ecf0f1";
            name.style.fontWeight = "bold";
            name.style.marginBottom = "6px";
            name.innerText = enemy.name;
            info.appendChild(name);
            
            // Description
            const desc = document.createElement("div");
            desc.style.fontSize = "10px";
            desc.style.color = "#bdc3c7";
            desc.style.marginBottom = "8px";
            desc.style.lineHeight = "1.4";
            desc.innerText = enemy.description;
            info.appendChild(desc);
            
            // Stats
            const stats = document.createElement("div");
            stats.style.fontSize = "9px";
            stats.style.color = "#f39c12";
            stats.style.display = "flex";
            stats.style.gap = "12px";
            stats.innerHTML = `<span>HP: ${enemy.stats.hp}</span><span>SPD: ${enemy.stats.speed}</span><span>DMG: ${enemy.stats.damage}</span>`;
            info.appendChild(stats);
            
            entry.appendChild(info);
            bestiaryPanel.appendChild(entry);
        });
        
        document.body.appendChild(bestiaryPanel);
    }
    bestiaryPanel.style.display = "block";
}

function setupCanvas() {
    let w, h;

    // Determine size based on state
    if (onTitleScreen) {
        w = 800;
        h = 800;
    } else if (inMenu) {
        const cardsPerRow = 3;
        const cardW = 220; const cardH = 200;
        const startX = 80; const startY = 140; const gap = 30;
        const rows = Math.max(1, Math.ceil(MAP_LIST.length / cardsPerRow));
        w = Math.max(MENU_CONFIG.width, startX * 2 + cardsPerRow * cardW + (cardsPerRow - 1) * gap);
        h = Math.max(MENU_CONFIG.height, startY + rows * cardH + (rows - 1) * gap + 40);
    } else {
        if (!state.grid || state.grid.length === 0) return;
        h = state.grid.length * TILE_SIZE;
        w = state.grid[0].length * TILE_SIZE;
    }

    if (!canvas) {
        canvas = document.createElement("canvas");
        document.body.appendChild(canvas);
        ctx = canvas.getContext("2d");
        ctx.imageSmoothingEnabled = false; 
        const container = document.getElementById("canvas-container");
        if (container) container.appendChild(canvas);
        else document.body.appendChild(canvas);
    }

    if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w;
        canvas.height = h;
    }
}

export function drawTitleScreen() {
    // Hide catalogue on title screen
    const catalogue = document.getElementById("catalog-container");
    if (catalogue) catalogue.style.display = "none";
    
    // Hide bestiary on title screen
    const bestiary = document.getElementById("bestiary-panel");
    if (bestiary) bestiary.style.display = "none";

    setupCanvas();
    if (!ctx) return;

    // Draw background
    ctx.fillStyle = "#000000";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const titleAsset = ASSETS["title"];
    if (titleAsset && titleAsset.img && titleAsset.img.complete) {
        const imgWidth = titleAsset.img.width;
        const imgHeight = titleAsset.img.height;
        const canvasRatio = canvas.width / canvas.height;
        const imgRatio = imgWidth / imgHeight;
        
        let drawWidth, drawHeight, drawX, drawY;
        
        // Scale to fit entirely within the canvas (contain mode - shows full image)
        if (canvasRatio > imgRatio) {
            drawHeight = canvas.height;
            drawWidth = canvas.height * imgRatio;
            drawX = (canvas.width - drawWidth) / 2;
            drawY = 0;
        } else {
            drawWidth = canvas.width;
            drawHeight = canvas.width / imgRatio;
            drawX = 0;
            drawY = (canvas.height - drawHeight) / 2;
        }
        
        ctx.drawImage(titleAsset.img, drawX, drawY, drawWidth, drawHeight);
    }

    // Draw splash text if available
    if (currentSplashText) {
        updateSplashFlash();
        let splashElement = document.getElementById("splash-text");
        if (!splashElement) {
            splashElement = document.createElement("div");
            splashElement.id = "splash-text";
            splashElement.style.position = "fixed";
            splashElement.style.top = "80px";
            splashElement.style.right = "40px";
            splashElement.style.color = "#FFD700";
            splashElement.style.fontSize = "30px";
            splashElement.style.fontFamily = FONT_NAME;
            splashElement.style.fontWeight = "bold";
            splashElement.style.textAlign = "center";
            splashElement.style.whiteSpace = "nowrap";
            splashElement.style.textShadow = "3px 3px 8px rgba(0, 0, 0, 0.9)";
            splashElement.style.zIndex = "100";
            splashElement.style.transform = "rotate(15deg)";
            splashElement.style.transformOrigin = "top right";
            splashElement.style.pointerEvents = "none";
            
            document.body.appendChild(splashElement);
        }
        splashElement.innerText = currentSplashText;
        splashElement.style.opacity = splashFlashOpacity;
        splashElement.style.display = "block";
    }

    // Create or update text element under canvas
    let titleText = document.getElementById("title-text");
    if (!titleText) {
        titleText = document.createElement("div");
        titleText.id = "title-text";
        titleText.style.position = "fixed";
        titleText.style.color = "#ecf0f1";
        titleText.style.fontSize = "24px";
        titleText.style.fontFamily = FONT_NAME;
        titleText.style.textAlign = "center";
        titleText.style.width = "100%";
        titleText.style.marginTop = "20px";
        titleText.innerText = "Click anywhere to start";
        
        const container = document.getElementById("canvas-container");
        if (container) {
            container.appendChild(titleText);
        } else {
            document.body.appendChild(titleText);
        }
    }
    titleText.style.display = "block";
}

export function drawMainMenu() {
    // Hide title text when leaving title screen
    const titleText = document.getElementById("title-text");
    if (titleText) {
        titleText.style.display = "none";
    }

    // Hide splash text when leaving title screen
    const splashElement = document.getElementById("splash-text");
    if (splashElement) {
        splashElement.style.display = "none";
    }

    // Hide catalogue on menu screen
    const catalogue = document.getElementById("catalog-container");
    if (catalogue) catalogue.style.display = "none";
    
    setupCanvas();
    setupCanvas(); 
    if (!ctx) return;

    // Dark blue background
    ctx.fillStyle = "#2c3e50";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Title
    ctx.fillStyle = "#f1c40f"; // Gold title
    ctx.font = `30px ${FONT_NAME}`; 
    ctx.textAlign = "center";
    ctx.fillText("SUNKEN TREASURE CHEST", canvas.width / 2, 80);

    if (MAP_LIST && MAP_LIST.length > 0) {
        const cardsPerRow = 3;
        const cardW = 220;
        const cardH = 200;
        const startX = 80;
        const startY = 140;
        const gap = 30;

        MAP_LIST.forEach((map, idx) => {
            const row = Math.floor(idx / cardsPerRow);
            const col = idx % cardsPerRow;
            const x = startX + col * (cardW + gap);
            const y = startY + row * (cardH + gap);
            const isHover = !!map._hover;

            drawPixelButton(
                ctx, x, y, cardW, cardH, isHover, 
                map.name || `Level ${map.id}`, 
                `Waves: ${map.nb_waves ?? 'N/A'}`
            );

            // Draw Preview Grid on top of the button
            const previewSize = 120; // Slightly smaller to fit inside button borders
            const grid = map.grid || [];
            const rows = grid.length;
            const cols = rows > 0 ? grid[0].length : 0;
            const cellSize = rows && cols ? Math.min(previewSize / rows, previewSize / cols) : 0;
            const offsetX = x + (cardW - cellSize * cols) / 2;
            const offsetY = y + 65; // Push down below text

            // Draw a black background behind the preview for contrast
            ctx.fillStyle = "#000000";
            ctx.fillRect(offsetX - 2, offsetY - 2, (cellSize * cols) + 4, (cellSize * rows) + 4);

            for (let r = 0; r < rows; r++) {
                for (let c = 0; c < cols; c++) {
                    const key = grid[r][c];
                    const color = TILE_PREVIEW_COLORS[key] || "#7f8c8d";
                    ctx.fillStyle = color;
                    ctx.fillRect(offsetX + c * cellSize, offsetY + r * cellSize, cellSize, cellSize);
                }
            }

            map._card = { x, y, w: cardW, h: cardH };
            
            if (isHover) {
                ctx.font = `10px ${FONT_NAME}`;
                ctx.fillStyle = "#f1c40f"; // Gold text for CTA
                ctx.fillText("CLICK TO START", x + cardW / 2, y + cardH - 12);
            }
        });
    } else {
        // Static Buttons Fallback
        MENU_CONFIG.buttons.forEach(btn => {
            const isHover = hoveredStaticButtonId === btn.id;
            drawPixelButton(ctx, btn.x, btn.y, btn.w, btn.h, isHover, btn.label);
        });
    }

    // Draw Bestiary on top
    drawBestiary();
}

export function drawGameInfo() {
    // Top-right: Timer and Wave Info
    let timerBar = document.getElementById("timer-bar");
    if (!timerBar) {
        timerBar = document.createElement("div");
        timerBar.id = "timer-bar";
        timerBar.style.position = "fixed";
        timerBar.style.top = "12px";
        timerBar.style.right = "12px";
        timerBar.style.padding = "16px 24px";
        timerBar.style.background = "#2c3e50";
        timerBar.style.color = "#ecf0f1";
        timerBar.style.fontFamily = `${FONT_NAME}, cursive`; 
        timerBar.style.border = "4px solid #34495e"; 
        timerBar.style.boxShadow = "inset 0 0 0 4px #ecf0f1";
        timerBar.style.display = "flex";
        timerBar.style.flexDirection = "column";
        timerBar.style.gap = "12px";
        timerBar.style.zIndex = "999";
        timerBar.style.imageRendering = "pixelated";
        timerBar.style.textAlign = "center";
        
        // Create static structure
        const timerDiv = document.createElement("div");
        timerDiv.id = "timer-text";
        timerDiv.style.fontSize = "28px";
        timerDiv.style.lineHeight = "1.2";
        timerDiv.style.color = "#f1c40f";
        timerDiv.style.fontWeight = "bold";
        
        const waveDiv = document.createElement("div");
        waveDiv.id = "wave-text";
        waveDiv.style.fontSize = "14px";
        waveDiv.style.lineHeight = "1.2";
        waveDiv.style.textTransform = "uppercase";
        
        const skipBtn = document.createElement("button");
        skipBtn.id = "skip-wave-btn";
        skipBtn.className = "menu-btn menu-btn--skip";
        skipBtn.style.marginTop = "8px";
        skipBtn.innerText = "Advance to Wave";
        
        // Add event listeners
        skipBtn.onmouseenter = () => {
            skipBtn.style.transform = "translateY(-1px)";
            skipBtn.style.boxShadow = "0 5px 0 #d68910";
        };
        skipBtn.onmouseleave = () => {
            skipBtn.style.transform = "translateY(0)";
            skipBtn.style.boxShadow = "0 4px 0 #d68910";
        };
        skipBtn.onclick = () => {
            state.time_until_next_wave = 0;
            playSound("/assets/sound/alert.mp3",0.5)
            console.log("Skipping to next wave");
        };
        
        timerBar.appendChild(timerDiv);
        timerBar.appendChild(waveDiv);
        timerBar.appendChild(skipBtn);
        document.body.appendChild(timerBar);
    }
    
    // Update dynamic content
    const rawSeconds = Math.max(0, Math.ceil(state.time_until_next_wave ?? 0));
    const seconds = rawSeconds;
    const mm = String(Math.floor(seconds / 60)).padStart(2, "0");
    const ss = String(seconds % 60).padStart(2, "0");
    const timerText = seconds === 0 ? "IN PROGRESS" : `${mm}:${ss}`;
    const totalWaves = Array.isArray(state.waves) ? state.waves.length : null;
    const currentWaveIndex = typeof state.current_wave === "number" ? state.current_wave : 0;
    const waveLabel = totalWaves !== null ? `WAVE ${currentWaveIndex}/${totalWaves}` : "WAVE: N/A";

    const timerTextEl = document.getElementById("timer-text");
    const waveTextEl = document.getElementById("wave-text");
    const skipWaveBtn = document.getElementById("skip-wave-btn");
    
    if (timerTextEl) timerTextEl.innerText = timerText;
    if (waveTextEl) waveTextEl.innerText = waveLabel;
    
    // Hide skip button during fighting phase (when timer is 0)
    if (skipWaveBtn) {
        skipWaveBtn.style.display = seconds === 0 ? "none" : "block";
    }

    // Bottom-right: Score and Gold Info
    let scoreBar = document.getElementById("score-bar");
    if (!scoreBar) {
        scoreBar = document.createElement("div");
        scoreBar.id = "score-bar";
        scoreBar.style.position = "fixed";
        scoreBar.style.bottom = "12px";
        scoreBar.style.right = "12px";
        scoreBar.style.padding = "16px 24px";
        scoreBar.style.background = "#2c3e50";
        scoreBar.style.color = "#ecf0f1";
        scoreBar.style.fontFamily = `${FONT_NAME}, cursive`; 
        scoreBar.style.border = "4px solid #34495e"; 
        scoreBar.style.boxShadow = "inset 0 0 0 4px #ecf0f1";
        scoreBar.style.display = "flex";
        scoreBar.style.flexDirection = "column";
        scoreBar.style.gap = "12px";
        scoreBar.style.zIndex = "999";
        scoreBar.style.imageRendering = "pixelated";
        scoreBar.style.textAlign = "center";
        document.body.appendChild(scoreBar);
    }

    scoreBar.innerHTML = `
        <div style="font-size: 20px; line-height: 1.2; color: #3498db; font-weight: bold;">Score: ${state.score}</div>
        <div style="font-size: 16px; line-height: 1.2; color: #f39c12;">Gold: ${state.gold}</div>
    `;

    // Top-left: Menu Buttons
    let menuButtonsBar = document.getElementById("menu-buttons-bar");
    if (!menuButtonsBar) {
        menuButtonsBar = document.createElement("div");
        menuButtonsBar.id = "menu-buttons-bar";
        menuButtonsBar.style.position = "fixed";
        menuButtonsBar.style.top = "12px";
        menuButtonsBar.style.left = "12px";
        menuButtonsBar.style.padding = "16px 20px";
        menuButtonsBar.style.background = "#2c3e50";
        menuButtonsBar.style.color = "#ecf0f1";
        menuButtonsBar.style.fontFamily = `${FONT_NAME}, cursive`; 
        menuButtonsBar.style.border = "4px solid #34495e"; 
        menuButtonsBar.style.boxShadow = "inset 0 0 0 4px #ecf0f1";
        menuButtonsBar.style.display = "flex";
        menuButtonsBar.style.flexDirection = "column";
        menuButtonsBar.style.gap = "12px";
        menuButtonsBar.style.zIndex = "999";
        menuButtonsBar.style.imageRendering = "pixelated";
        
        menuButtonsBar.innerHTML = `
            <button id="back-menu-btn" class="menu-btn menu-btn--back">Back Menu</button>
            <button id="save-game-btn" class="menu-btn menu-btn--save">Save Game</button>
            <button id="load-game-btn" class="menu-btn menu-btn--load">Load Game</button>
        `;

        const backBtn = menuButtonsBar.querySelector("#back-menu-btn");
        const saveBtn = menuButtonsBar.querySelector("#save-game-btn");
        const loadBtn = menuButtonsBar.querySelector("#load-game-btn");

        if (backBtn) {
            backBtn.onmouseenter = () => {
                backBtn.style.transform = "translateY(-1px)";
                backBtn.style.boxShadow = "0 5px 0 #8f2d28";
            };
            backBtn.onmouseleave = () => {
                backBtn.style.transform = "translateY(0)";
                backBtn.style.boxShadow = "0 4px 0 #b53a30";
            };
            backBtn.onclick = () => {
                window.location.reload();
            };
        }

        if (saveBtn) {
            saveBtn.onmouseenter = () => {
                saveBtn.style.transform = "translateY(-1px)";
                saveBtn.style.boxShadow = "0 5px 0 #1b6f3f";
            };
            saveBtn.onmouseleave = () => {
                saveBtn.style.transform = "translateY(0)";
                saveBtn.style.boxShadow = "0 4px 0 #1f8a4c";
            };
            saveBtn.onclick = () => {
                save_state();
            };
        }

        if (loadBtn) {
            loadBtn.onmouseenter = () => {
                loadBtn.style.transform = "translateY(-1px)";
                loadBtn.style.boxShadow = "0 5px 0 #1857a0";
            };
            loadBtn.onmouseleave = () => {
                loadBtn.style.transform = "translateY(0)";
                loadBtn.style.boxShadow = "0 4px 0 #2980b9";
            };
            loadBtn.onclick = () => {
                load_state();
            };
        }

        document.body.appendChild(menuButtonsBar);
    }
}

export function draw_gems(treasure, treasure_pos) {
    if (!treasure) return;
    treasure.forEach(jewel => {
        if (jewel.position[0] == treasure_pos[0] && jewel.position[1] == treasure_pos[1]) return;
        if (jewel.present === false) return;
        const asset = ASSETS["jewel"];
        if (!asset) return;
        draw_asset(asset, jewel.position[1], jewel.position[0]);
    });
}

function updateEndOverlay() {
    const existing = document.getElementById("end-overlay");
    if (!state.finished) {
        if (existing) existing.remove();
        const gameoverOverlay = document.getElementById("gameover-overlay");
        if (gameoverOverlay) gameoverOverlay.remove();
        return;
    }

    if (!state.won && !state.gameoverShown) {
        const gameoverOverlay = document.getElementById("gameover-overlay");
        if (!gameoverOverlay) {
            state.gameoverShown = true;
            
            const overlay = document.createElement("div");
            overlay.id = "gameover-overlay";
            overlay.style.position = "fixed";
            overlay.style.top = "0";
            overlay.style.left = "0";
            overlay.style.width = "100vw";
            overlay.style.height = "100vh";
            overlay.style.display = "flex";
            overlay.style.alignItems = "center";
            overlay.style.justifyContent = "center";
            overlay.style.background = "rgba(0,0,0,0.9)";
            overlay.style.zIndex = "1999";
            overlay.style.cursor = "pointer";

            const img = document.createElement("img");
            img.src = ASSETS["gameover"].src;
            img.style.maxWidth = "100vw";
            img.style.maxHeight = "100vh";
            img.style.width = "100%";
            img.style.height = "100%";
            img.style.objectFit = "contain";

            const skipText = document.createElement("div");
            skipText.style.position = "absolute";
            skipText.style.bottom = "20px";
            skipText.style.color = "#f1c40f";
            skipText.style.fontFamily = FONT_NAME;
            skipText.style.fontSize = "12px";
            skipText.innerText = "Click to continue";

            overlay.appendChild(img);
            overlay.appendChild(skipText);
            
            // Add click handler to skip gameover animation
            overlay.onclick = () => {
                overlay.remove();
            };
            
            // Play gameover music
            playSound('/assets/sound/gameover.mp3');
            
            document.body.appendChild(overlay);
        }
        return;
    }

    const title = state.won ? "YOU WON!" : "GAME OVER";
    let jewelsLeft = 0;
    for (const jewel of state.treasure) {
        if (jewel.present) jewelsLeft++;
    }
    const subtitle = state.won 
        ? `Treasure secured. ${jewelsLeft} jewel${jewelsLeft !== 1 ? 's' : ''} remaining.`
        : "Try again to protect the treasure.";

    if (!state.won) {
        // For game over (loss), show a small corner panel
        const cornerPanel = document.getElementById("gameover-corner-panel");
        if (!cornerPanel) {
            const panel = document.createElement("div");
            panel.id = "gameover-corner-panel";
            panel.style.position = "fixed";
            panel.style.bottom = "20px";
            panel.style.right = "20px";
            panel.style.background = "#2c3e50";
            panel.style.border = "4px solid #f1c40f";
            panel.style.boxShadow = "0 8px 0 #1a252f";
            panel.style.padding = "16px 20px";
            panel.style.borderRadius = "10px";
            panel.style.textAlign = "center";
            panel.style.color = "#ecf0f1";
            panel.style.fontFamily = FONT_NAME;
            panel.style.minWidth = "200px";
            panel.style.zIndex = "2001";

            const titleEl = document.createElement("div");
            titleEl.style.fontSize = "14px";
            titleEl.style.marginBottom = "8px";
            titleEl.innerText = "GAME OVER";

            const scoreEl = document.createElement("div");
            scoreEl.style.fontSize = "12px";
            scoreEl.style.marginBottom = "12px";
            scoreEl.innerText = `Score: ${state.score}`;

            const btn = document.createElement("button");
            btn.innerText = "Back to Menu";
            btn.style.padding = "8px 12px";
            btn.style.fontFamily = FONT_NAME;
            btn.style.fontSize = "10px";
            btn.style.color = "#2c3e50";
            btn.style.background = "#f1c40f";
            btn.style.border = "3px solid #d4a00d";
            btn.style.borderRadius = "6px";
            btn.style.cursor = "pointer";
            btn.style.transition = "transform 120ms ease, box-shadow 120ms ease";
            btn.style.boxShadow = "0 4px 0 #a67c0a";
            btn.onmouseenter = () => {
                btn.style.transform = "translateY(-2px)";
                btn.style.boxShadow = "0 6px 0 #a67c0a";
            };
            btn.onmouseleave = () => {
                btn.style.transform = "translateY(0)";
                btn.style.boxShadow = "0 4px 0 #a67c0a";
            };
            btn.onclick = () => {
                window.location.reload();
            };

            panel.appendChild(titleEl);
            panel.appendChild(scoreEl);
            panel.appendChild(btn);
            document.body.appendChild(panel);
        }
        return;
    }

    if (!existing) {
        const overlay = document.createElement("div");
        overlay.id = "end-overlay";
        overlay.style.position = "fixed";
        overlay.style.top = "0";
        overlay.style.left = "0";
        overlay.style.width = "100vw";
        overlay.style.height = "100vh";
        overlay.style.display = "flex";
        overlay.style.alignItems = "center";
        overlay.style.justifyContent = "center";
        overlay.style.background = "rgba(0,0,0,0.75)";
        overlay.style.zIndex = "2000";
        overlay.style.backdropFilter = "blur(2px)";
        overlay.style.flexDirection = "row";
        overlay.style.gap = "24px";

        const panel = document.createElement("div");
        panel.style.background = "#2c3e50";
        panel.style.border = "4px solid #f1c40f";
        panel.style.boxShadow = "0 8px 0 #1a252f";
        panel.style.padding = "24px 28px";
        panel.style.borderRadius = "10px";
        panel.style.textAlign = "center";
        panel.style.color = "#ecf0f1";
        panel.style.fontFamily = FONT_NAME;
        panel.style.minWidth = "320px";

        const titleEl = document.createElement("div");
        titleEl.id = "end-overlay-title";
        titleEl.style.fontSize = "22px";
        titleEl.style.marginBottom = "10px";

        const subEl = document.createElement("div");
        subEl.id = "end-overlay-sub";
        subEl.style.fontSize = "12px";
        subEl.style.marginBottom = "8px";

        const scoreEl = document.createElement("div");
        scoreEl.id = "end-overlay-score";
        scoreEl.style.fontSize = "12px";
        scoreEl.style.marginBottom = "16px";

        const creditsImg = document.createElement("img");
        creditsImg.id = "end-overlay-credits";
        creditsImg.style.width = "360px";
        creditsImg.style.maxWidth = "40vw";
        creditsImg.style.maxHeight = "70vh";
        creditsImg.style.objectFit = "contain";
        creditsImg.style.border = "4px solid #f1c40f";
        creditsImg.style.borderRadius = "12px";
        creditsImg.style.boxShadow = "0 8px 0 #1a252f";
        creditsImg.style.display = "none"; // Only shown on victory
        const creditsAsset = ASSETS["credits"];
        if (creditsAsset && creditsAsset.src) {
            creditsImg.src = creditsAsset.src;
        }

        const btn = document.createElement("button");
        btn.id = "end-overlay-btn";
        btn.innerText = "Back to Menu";
        btn.style.padding = "10px 16px";
        btn.style.fontFamily = FONT_NAME;
        btn.style.fontSize = "10px";
        btn.style.color = "#2c3e50";
        btn.style.background = "#f1c40f";
        btn.style.border = "3px solid #d4a00d";
        btn.style.borderRadius = "6px";
        btn.style.cursor = "pointer";
        btn.style.transition = "transform 120ms ease, box-shadow 120ms ease";
        btn.style.boxShadow = "0 4px 0 #a67c0a";
        btn.onmouseenter = () => {
            btn.style.transform = "translateY(-2px)";
            btn.style.boxShadow = "0 6px 0 #a67c0a";
        };
        btn.onmouseleave = () => {
            btn.style.transform = "translateY(0)";
            btn.style.boxShadow = "0 4px 0 #a67c0a";
        };
        btn.onclick = () => {
            window.location.reload();
        };

        panel.appendChild(titleEl);
        panel.appendChild(subEl);
        panel.appendChild(scoreEl);
        panel.appendChild(btn);
        overlay.appendChild(panel);
        overlay.appendChild(creditsImg);
        document.body.appendChild(overlay);
    }

    const titleEl = document.getElementById("end-overlay-title");
    const subEl = document.getElementById("end-overlay-sub");
    const scoreEl = document.getElementById("end-overlay-score");
    const creditsImg = document.getElementById("end-overlay-credits");
    const overlay = document.getElementById("end-overlay");
    if (titleEl) titleEl.innerText = title;
    if (subEl) subEl.innerText = subtitle;
    if (scoreEl) scoreEl.innerText = `Score: ${state.score}`;
    if (overlay) {
        overlay.style.flexDirection = "row";
        overlay.style.gap = "24px";
    }
    if (creditsImg) creditsImg.style.display = state.won ? "block" : "none";
}

export function drawCutscene() {
    // Hide canvas and create HTML overlay for animated GIF
    const canvas = document.querySelector("canvas");
    if (canvas) canvas.style.display = "none";

    let cutsceneOverlay = document.getElementById("cutscene-overlay");
    if (!cutsceneOverlay) {
        cutsceneOverlay = document.createElement("div");
        cutsceneOverlay.id = "cutscene-overlay";
        cutsceneOverlay.style.position = "fixed";
        cutsceneOverlay.style.top = "0";
        cutsceneOverlay.style.left = "0";
        cutsceneOverlay.style.width = "100vw";
        cutsceneOverlay.style.height = "100vh";
        cutsceneOverlay.style.display = "flex";
        cutsceneOverlay.style.flexDirection = "column";
        cutsceneOverlay.style.alignItems = "center";
        cutsceneOverlay.style.justifyContent = "center";
        cutsceneOverlay.style.background = "#000000";
        cutsceneOverlay.style.zIndex = "1500";
        cutsceneOverlay.style.cursor = "pointer";

        const img = document.createElement("img");
        img.src = "./assets/cutscene.gif";
        img.style.width = "100%";
        img.style.height = "100%";
        img.style.objectFit = "cover";
        img.style.imageRendering = "auto";

        const skipText = document.createElement("div");
        skipText.style.position = "absolute";
        skipText.style.bottom = "30px";
        skipText.style.color = "#ecf0f1";
        skipText.style.fontFamily = FONT_NAME;
        skipText.style.fontSize = "12px";
        skipText.innerText = "Click to skip";

        cutsceneOverlay.appendChild(img);
        cutsceneOverlay.appendChild(skipText);
        
        // Add click handler to skip cutscene
        cutsceneOverlay.onclick = () => {
            completeCutsceneAndStartGame();
        };
        
        // Play intro music and auto-advance when it ends
        const introAudio = new Audio('/assets/sound/intro.mp3');
        introAudio.play().catch((error) => {
            console.error("Audio playback failed:", error);
        });
        introAudio.addEventListener('ended', () => {
            completeCutsceneAndStartGame();
        });
        
        document.body.appendChild(cutsceneOverlay);
    }
    cutsceneOverlay.style.display = "flex";
}

function hideCutscene() {
    const cutsceneOverlay = document.getElementById("cutscene-overlay");
    if (cutsceneOverlay) cutsceneOverlay.style.display = "none";
    
    const canvas = document.querySelector("canvas");
    if (canvas) canvas.style.display = "block";
}

export function draw() {
    // 1. Check if we are on the title screen
    if (onTitleScreen) {
        drawTitleScreen();
        return;
    }

    // 2. Check if we are showing cutscene
    if (inCutscene) {
        drawCutscene();
        return;
    }

    // Hide cutscene overlay if we're past cutscene
    hideCutscene();

    // 3. Check if we are in the Menu
    if (inMenu) {
        drawMainMenu();
        return;
    }

    // 4. Otherwise, draw the Game
    // Show catalogue during game
    const catalogue = document.getElementById("catalog-container");
    if (catalogue) catalogue.style.display = "block";
    
    // Hide bestiary during game
    const bestiary = document.getElementById("bestiary-panel");
    if (bestiary) bestiary.style.display = "none";

    setupCanvas();
    if (!ctx) return; 

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    var treasure_pos = [0, 0];
    if (state.grid) {
        const to_draw = transform_mat(state.grid); 
        for (let y = 0; y < to_draw.length; y++) {
            for (let x = 0; x < to_draw[y].length; x++) {
                const tileKey = to_draw[y][x]; 
                const asset = ASSETS[tileKey];
                if (asset) draw_asset(asset, x, y);

                if (tileKey === "treasure") {
                    treasure_pos = [y, x];
                }
            }
        }
    }

    if (state.treasure) {
        ctx.fillStyle = "white";
        ctx.font = `10px ${FONT_NAME}`; 
        ctx.textAlign = "center";
        const textX = pixel(treasure_pos[1]) + TILE_SIZE / 2;
        const textY = pixel(treasure_pos[0]) + TILE_SIZE / 2 + 5; 
        var n = 0;
        for (let i = 0; i < state.treasure.length; i++) {
            const jewel = state.treasure[i];
            if (jewel.position[0] == treasure_pos[0] && jewel.position[1] == treasure_pos[1]) {
                n += 1;
            }
        }
        ctx.fillText(`${n}`, textX, textY);
    }

    draw_entities(state.buildings);
    draw_entities(state.monsters);  
    draw_entities(state.heros);
    draw_gems(state.treasure, treasure_pos);
    
    drawGameInfo();
    updateEndOverlay();

    if (state.selectedPos && Array.isArray(placeable_buildings) && placeable_buildings.length > 0) {
        const { x, y } = state.selectedPos;
        ctx.save();
        ctx.strokeStyle = '#e74c3c'; // Brighter red for cursor
        ctx.lineWidth = 4; // Thicker cursor
        ctx.setLineDash([0]); // Solid line for pixel art feel
        // Draw corners only logic could go here for more style, but solid rect is fine
        ctx.strokeRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
        ctx.restore();
    }
}