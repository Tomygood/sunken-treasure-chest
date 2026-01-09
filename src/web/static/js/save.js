import { draw, loadAssets, loadMapList } from './render.js';
import { startGame } from './network.js';
import { initInput } from './input.js'; // <--- 1. Import this
import { state, advence_state, setHasChanged, updateGlobalState } from './state.js';


export const inputFile = document.getElementById("LoadButton");

export function loadstate(json_txt){
    json_json = JSON.parse(json_txt)
    updateGlobalState(json_json)
    setHasChanged(true);
}

export function load_state() {
    // Create a hidden file input element
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.json';
    fileInput.style.display = 'none';
    
    fileInput.onchange = (event) => {
        const file = event.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const json_txt = e.target.result;
                const json_data = JSON.parse(json_txt);
                updateGlobalState(json_data);
                draw(); // Redraw after loading
                console.log('Game state loaded successfully');
            } catch (error) {
                console.error('Error loading save file:', error);
                alert('Failed to load save file. Please make sure it is a valid save file.');
            }
        };
        reader.readAsText(file);
        
        // Clean up
        document.body.removeChild(fileInput);
    };
    
    // Trigger file dialog
    document.body.appendChild(fileInput);
    fileInput.click();
}



export function save_state(){
    const state_txt = JSON.stringify(state)
    const dllink = document.createElement('a')
    const blb = new Blob([state_txt],{type:'test/plain'})
    const fileURL = URL.createObjectURL(blb)
    dllink.href = fileURL
    dllink.download = 'save.json'
    document.body.appendChild(dllink)
    dllink.click()
    URL.revokeObjectURL(fileURL)
}
