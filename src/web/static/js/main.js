import { draw, loadAssets, loadMapList } from './render.js';
import { startGame } from './network.js';
import { initInput } from './input.js'; 
import { playSound } from './sound.js';
import { state, advence_state, setHasChanged, inCutscene, onTitleScreen, inMenu, loadSplashTexts } from './state.js';



async function init() {
    console.log("Initializing Application...");
    
    const handleLevelSelection = async (levelId) => {
        console.log(`Main.js received request to start Level ${levelId}`);
        await startGame(levelId);
        state.state = 0;
    };

    initInput(handleLevelSelection); 

    console.log("Preloading images...");
    await loadAssets();
    await loadMapList();
    await loadSplashTexts();
    
    console.log("Assets loaded. Displaying Main Menu.");
    
    let lastAdvanceTime = 0;
    const ADVANCE_INTERVAL = 100; // 0.1 second in milliseconds
    let lastCountdownTime = 0;
    const COUNTDOWN_INTERVAL = 1000; // 1 second in milliseconds

            

    const gameLoop = async (currentTime) => {
        // Skip game logic during title, menu, or cutscene
        if (onTitleScreen || inMenu || inCutscene) {
            draw();
            requestAnimationFrame(gameLoop);
            return;
        }

        // Decrease countdown every second during building phase
        if (!state.finished && state.state === 0) {
            if (currentTime - lastCountdownTime >= COUNTDOWN_INTERVAL) {
                if (typeof state.time_until_next_wave === 'number' && state.time_until_next_wave > 0) {
                    if (state.time_until_next_wave === 1) {
                        playSound("/assets/sound/alert.mp3",0.5)
                    }
                    state.time_until_next_wave -= 1;
                    setHasChanged(true)
                }
                lastCountdownTime = currentTime;
            }
        }
        if ((!state.finished) && ((state.state === 1 && currentTime - lastAdvanceTime >= ADVANCE_INTERVAL) || (state.time_until_next_wave <= 0 && state.state === 0 && currentTime - lastAdvanceTime >= ADVANCE_INTERVAL))) {
            await advence_state();
            lastAdvanceTime = currentTime;
        }
        draw();
        requestAnimationFrame(gameLoop);
    };
    
    requestAnimationFrame(gameLoop); 
}


// Start the app
init();
