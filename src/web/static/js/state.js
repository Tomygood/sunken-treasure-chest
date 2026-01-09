import { ASSETS } from './config.js';
import { playSound } from './sound.js';
// The single source of truth for the game data
export const state = {
    grid: [],         
    monsters: [],
    heros: [],
    buildings: [],
    treasure: [],
    gold: 1000,
    score: 0,
    time_until_next_wave: 0,
    wave_clock: 0,
    heros_left_to_spawn: 0,
    finished: false,
    won: false,
    gameoverShown: false,
};


const nexts = []
const next_nexts = []
export let nextTick = 0
export let HasChanged = false

const FONT_NAME = '"Press Start 2P", "Courier New", monospace';

// Splash text state
export let splashTexts = [];
export let currentSplashText = "";
export let splashFlashOpacity = 1;
const SPLASH_FLASH_DURATION = 3000; // 3 seconds
let splashFlashStart = 0;

export async function loadSplashTexts() {
    try {
        const response = await fetch("/splash-texts");
        if (!response.ok) throw new Error(`Failed to load splash texts: ${response.status}`);
        splashTexts = await response.json();
        selectRandomSplashText();
    } catch (error) {
        console.error("Failed to load splash texts:", error);
        splashTexts = ["Error loading splash texts!"];
        currentSplashText = splashTexts[0];
    }
}

export function selectRandomSplashText() {
    if (splashTexts.length > 0) {
        currentSplashText = splashTexts[Math.floor(Math.random() * splashTexts.length)];
        splashFlashStart = Date.now();
        splashFlashOpacity = 1;
    }
}

export function updateSplashFlash() {
    const elapsed = Date.now() - splashFlashStart;
    // Loop the flash animation
    const progress = (elapsed % SPLASH_FLASH_DURATION) / SPLASH_FLASH_DURATION * Math.PI * 2;
    splashFlashOpacity = 0.5 + (Math.sin(progress) * 0.5);
}

export function setHasChanged(value) {
    HasChanged = value;
}

// Updates state with whatever data the server sent
// Controls if we are on Title Screen, Menu, Cutscene, or the Game
export let onTitleScreen = true;
export let inMenu = false;
export let inCutscene = false;

export function setOnTitleScreen(value) {
    onTitleScreen = value;
}

export function setInMenu(value) {
    inMenu = value;
}

export function setInCutscene(value) {
    inCutscene = value;
}

export const placeable_buildings = [];

export function updateGlobalState(newData) {
    Object.assign(state, newData);
}

async function add_to_nexts(){
    let state_copy =  structuredClone(state)


    if (nexts.length != 0){
        state_copy = update_with_tick(state_copy, nexts.length - 1)
    }


    const response = await fetch("/game-update", {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(state_copy)
    })


    if (!response.ok){
        throw new Error(`Response status: ${response.status}`);
    }
    const res = await response.json()
    next_nexts.splice(0,next_nexts.length,...res.changes)
}

function switch_nexts(){
    nexts.splice(0,nexts.length,...next_nexts)
}

export async function advence_state(){
    if (HasChanged){
        nexts.length = 0
        next_nexts.length = 0
        nextTick = 0
        await add_to_nexts()
        switch_nexts()
        HasChanged = false
        // Apply the first tick of new data immediately
        if (nexts.length > 0) {
            update_with_tick(state, 0)
            nextTick = 1
        }
        return
    }

    if (state.finished === true){
        return
    }
    
    // Check if we need to reset and fetch more ticks
    if (nextTick >= nexts.length){
        if (next_nexts.length == 0){
            await add_to_nexts()
        }
        switch_nexts()
        nextTick = 0
    }
    
    // Prefetch if running low on ticks
    if (nextTick === (nexts.length - 10)){
        await add_to_nexts()
    }
    
    if (nexts.length === 0){
        throw new Error(`No tick data available`);
    }
    
    if (nextTick >= nexts.length){
        throw new Error(`nextTick (${nextTick}) out of bounds for nexts (length ${nexts.length})`);
    }
    update_with_tick(state, nextTick)
    nextTick++
}

export function update_with_tick(st, next_i){
    st.buildings =   nexts[next_i].buildings
    st.heros =       nexts[next_i].heros
    st.monsters =    nexts[next_i].monsters
    st.treasure =    nexts[next_i].treasure
    st.heros_left_to_spawn = nexts[next_i].heros_left_to_spawn
    st.state = nexts[next_i].state
    st.finished = nexts[next_i].finished
    st.won = nexts[next_i].won
    st.time_until_next_wave = nexts[next_i].time_until_next_wave
    st.current_wave = nexts[next_i].current_wave
    st.gold = nexts[next_i].gold
    return st
}


export function update_placeable_buildings(newData){
// 1. On vide le tableau actuel sans changer sa référence
    placeable_buildings.length = 0; 
    
    // 2. Check if this is a single building (existing) or array of new buildings
    // Server returns [building, description] for existing, [[b1, d1], [b2, d2], ...] for new
    if (Array.isArray(newData) && newData.length === 2 && !Array.isArray(newData[0])) {
        // Single existing building - mark it as existing
        placeable_buildings.push([{...newData[0], isExisting: true}, newData[1]]);
    } else if (Array.isArray(newData)) {
        // Array of placeable buildings
        placeable_buildings.push(...newData);
    }
    
    // 3. IMPORTANT : On redessine le catalogue car les données ont changé
    drawBuildableBuildings();
}

export function drawBuildableBuildings() {
    const grid = document.getElementById("catalog-grid");
    if (!grid) return;

    // On vide le catalogue actuel avant de le redessiner
    grid.innerHTML = "";

    const makeEl = (tag, className, text) => {
        const el = document.createElement(tag);
        if (className) el.className = className;
        if (text !== undefined) el.innerText = text;
        return el;
    };

    placeable_buildings.forEach(([data, descriptionText]) => {
        const isExisting = data?.isExisting === true;
        const item = makeEl("div", "catalog-item");

        const img = document.createElement("img");
        const buildingAsset = ASSETS[data.name + data.level] || ASSETS[data.name];
        if (buildingAsset?.src) {
            img.src = buildingAsset.src;
            img.alt = data.name;
            img.className = "catalog-item__img";
        }

        const nameText = data.name + (isExisting ? ` (Lvl ${data.level || 1})` : "");
        const name = makeEl("div", "catalog-name", nameText);

        const priceValue = isExisting
            ? (() => {
                const currentLevel = data.level || 1;
                const upgradeCost = data.cost?.[currentLevel] || "Max";
                return upgradeCost !== "Max" ? `Upgrade: ${upgradeCost}` : "Max Level";
            })()
            : `$${data.cost[data.level - 1]}`;
        const price = makeEl("div", "catalog-price", priceValue);

        const description = makeEl("div", "catalog-desc", descriptionText || "No description available");

        const hp = Number.isFinite(data.hp) ? makeEl("div", "catalog-hp", `hp: ${data.hp}`) : null;

        item.appendChild(img);
        item.appendChild(name);
        item.appendChild(price);
        item.appendChild(description);
        if (hp) item.appendChild(hp);

        if (isExisting) {
            const buttonContainer = makeEl("div", "catalog-buttons");

            const currentLevel = data.level || 1;
            const isMaxLevel = data.cost?.[currentLevel] === undefined;

            const upgradeBtn = makeEl("button", "catalog-btn catalog-btn--upgrade", isMaxLevel ? "MAX" : "Upgrade");
            const upgradeCost = data.cost?.[currentLevel];
            const notEnoughGold = Number.isFinite(upgradeCost) && state.gold < upgradeCost;
            upgradeBtn.disabled = isMaxLevel || notEnoughGold;
            if (!isMaxLevel) {
                upgradeBtn.onclick = async () => {
                    if (notEnoughGold) return;
                    const pos = state.selectedPos;
                    if (!pos) return;
                    try {
                        const response = await fetch('/upgrade_building', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                            body: JSON.stringify({ game: state, x: pos.x, y: pos.y })
                        });
                        if (!response.ok) throw new Error(`Server Error: ${response.status}`);
                        const newData = await response.json();
                        updateGlobalState(newData);
                        setHasChanged(true);
                        playSound("/assets/sound/buybuilding.wav",0.5)
                        state.selectedPos = null;
                        placeable_buildings.length = 0;
                        drawBuildableBuildings();
                    } catch (error) {
                        console.error('Failed to upgrade building:', error);
                    }
                };
            }

            const deleteBtn = makeEl("button", "catalog-btn catalog-btn--delete", "Sell");
            deleteBtn.onclick = async () => {
                const pos = state.selectedPos;
                if (!pos) return;
                try {
                    const response = await fetch('/delete_building', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                        body: JSON.stringify({ game: state, x: pos.x, y: pos.y })
                    });
                    if (!response.ok) throw new Error(`Server Error: ${response.status}`);
                    const newData = await response.json();
                    updateGlobalState(newData);
                    setHasChanged(true);
                    state.selectedPos = null;
                    placeable_buildings.length = 0;
                    drawBuildableBuildings();
                } catch (error) {
                    console.error('Failed to delete building:', error);
                }
            };

            buttonContainer.appendChild(upgradeBtn);
            buttonContainer.appendChild(deleteBtn);
            item.appendChild(buttonContainer);
        } else {
            const placeCost = data.cost[data.level - 1];
            const notEnoughGold = Number.isFinite(placeCost) && state.gold < placeCost;
            if (notEnoughGold) {
                item.classList.add('catalog-item--disabled');
            }
            item.onclick = async () => {
                if (notEnoughGold) return;
                const selectedName = data?.name;
                state.selectedBuilding = selectedName;

                const pos = state.selectedPos;
                if (!pos) {
                    console.warn('No grid position selected for placement.');
                    return;
                }

                try {
                    const response = await fetch('/place_building', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        },
                        body: JSON.stringify({
                            game: state,
                            building: selectedName,
                            x: pos.x,
                            y: pos.y
                        })
                    });

                    if (!response.ok) throw new Error(`Server Error: ${response.status}`);
                    const newData = await response.json();
                    playSound("/assets/sound/buybuilding.wav",0.5)
                    updateGlobalState(newData);
                    setHasChanged(true);
                    state.selectedPos = null;
                    placeable_buildings.length = 0;
                    drawBuildableBuildings();
                } catch (error) {
                    console.error('Failed to place building:', error);
                }
            };
        }

        grid.appendChild(item);
    });
}
