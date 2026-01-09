import { TILE_SIZE } from './config.js';
import { getPlaceableBuildings, completeCutsceneAndStartGame } from './network.js'; 
import { inMenu, onTitleScreen, inCutscene, setOnTitleScreen, setInMenu, state } from './state.js'; 
import { getMenuCards, MENU_CONFIG, setHoveredStaticButton } from './render.js'; 
import {playSound} from './sound.js'

export function initInput(onStartGame) {
    console.log("Input system initialized.");

    document.addEventListener("click", (event) => {
        const canvas = document.querySelector("canvas");
            if (!canvas) return;

        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;

        const insideCanvas = (
            event.clientX >= rect.left && event.clientX <= rect.right &&
            event.clientY >= rect.top  && event.clientY <= rect.bottom
        );
        if (!insideCanvas) return;

        const mouseX = (event.clientX - rect.left) * scaleX;
        const mouseY = (event.clientY - rect.top) * scaleY;

        // --- TITLE SCREEN LOGIC ---
        if (onTitleScreen) {
            console.log("Title screen clicked - transitioning to menu");
            setOnTitleScreen(false);
            setInMenu(true);
            return;
        }

        // --- CUTSCENE LOGIC ---
        if (inCutscene) {
            console.log("Cutscene clicked - skipping to game");
            completeCutsceneAndStartGame();
            return;
        }

        // --- MENU LOGIC ---
        if (inMenu) {
            const cards = getMenuCards();
            if (cards.length > 0) {
                for (const card of cards) {
                    const area = card._card;
                    if (!area) continue;
                    const hit = mouseX >= area.x && mouseX <= area.x + area.w && mouseY >= area.y && mouseY <= area.y + area.h;
                    if (hit) {
                        console.log("Starting level", card.id, card.name);
                        if (onStartGame) onStartGame(card.id);
                        playSound("/assets/sound/hitHurt.wav",0.5);
                        break;
                    }
                }
            } else {
                // Fallback: static buttons
                MENU_CONFIG.buttons.forEach(btn => {
                    const hit = mouseX >= btn.x && mouseX <= btn.x + btn.w && mouseY >= btn.y && mouseY <= btn.y + btn.h;
                    if (hit) {
                        console.log(`Menu Clicked: Level ${btn.id}`);
                        if (onStartGame) onStartGame(btn.id);
                    }
                });
            }
            return;
        }

        // --- GAME LOGIC ---
        const gridX = Math.floor(mouseX / TILE_SIZE);
        const gridY = Math.floor(mouseY / TILE_SIZE);
        // Guard against out-of-grid clicks
        const gridH = Array.isArray(state.grid) ? state.grid.length : 0;
        const gridW = gridH > 0 && Array.isArray(state.grid[0]) ? state.grid[0].length : 0;
        if (gridX < 0 || gridY < 0 || gridX >= gridW || gridY >= gridH) return;

        state.selectedPos = { x: gridX, y: gridY };
        getPlaceableBuildings(gridY, gridX);
    });

    document.addEventListener("mousemove", (event) => {
        const canvas = document.querySelector("canvas");
        if (!canvas) return;
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        const mouseX = (event.clientX - rect.left) * scaleX;
        const mouseY = (event.clientY - rect.top) * scaleY;

        if (onTitleScreen || inCutscene || !inMenu) return;

        if (inMenu) {
            const cards = getMenuCards();
            let hovering = false;
            if (cards.length > 0) {
                for (const card of cards) {
                    const area = card._card;
                    if (!area) { card._hover = false; continue; }
                    const hit = mouseX >= area.x && mouseX <= area.x + area.w && mouseY >= area.y && mouseY <= area.y + area.h;
                    card._hover = hit;
                    if (hit) hovering = true;
                }
                setHoveredStaticButton(null);
            } else {
                let hoveredId = null;
                for (const btn of MENU_CONFIG.buttons) {
                    const hit = mouseX >= btn.x && mouseX <= btn.x + btn.w && mouseY >= btn.y && mouseY <= btn.y + btn.h;
                    if (hit) { hoveredId = btn.id; hovering = true; break; }
                }
                setHoveredStaticButton(hoveredId);
            }
            canvas.style.cursor = hovering ? 'pointer' : 'default';
        }
    });
}