import { updateGlobalState, state, update_placeable_buildings, setInMenu, setInCutscene } from './state.js';
import { draw, loadAssets } from './render.js';

let pendingMapData = null;

export async function startGame(mapId) {
    try {
        await loadAssets(); 
        
        const response = await fetch(`/get-startup-game/${mapId}`, {
            method: "GET",
            headers: { "Accept": "application/json" }
        });

        if (!response.ok) throw new Error(`Server Error: ${response.status}`);

        const data = await response.json();
        pendingMapData = data;

        // --- Show cutscene before game starts ---
        setInMenu(false);
        setInCutscene(true);
        // -----------------------------------------------------

        draw();
        
    } catch (error) {
        console.error("Failed to start game:", error);
    }
}

export function completeCutsceneAndStartGame() {
    if (pendingMapData) {
        updateGlobalState(pendingMapData);
        pendingMapData = null;
    }
    setInCutscene(false);
    state.state = 0; // Ensure countdown starts
    state.gameoverShown = false; // Reset gameover flag for new game
    draw();
}

// 2. POST: Send the current state back to the server
export async function sendUpdate() {
    try {

        const response = await fetch(`/update-game-state`, {
            method: "POST", 
            headers: { 
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(state) 
        });

        if (!response.ok) throw new Error(`Server Error: ${response.status}`);

        const newData = await response.json();
        updateGlobalState(newData);
        draw();

    } catch (error) {
        console.error("Failed to send update:", error);
    }
}


// 3. POST: Get buildings (Logs and updates global state only)
export async function getPlaceableBuildings(x, y) {
    try {
        const payload = {
            game: state,
            x: x,
            y: y
        };

        const response = await fetch("/get_building_placable", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`Server Error: ${response.status}`);

        const buildings = await response.json();
                
        // Update the global shared list
        update_placeable_buildings(buildings);

    } catch (error) {
        console.error("Failed to fetch placeable buildings:", error);
    }
}