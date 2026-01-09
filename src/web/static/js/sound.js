/**
 * Plays a sound file.
 * @param {string} url - The path to the audio file.
 * @param {number} volume - Optional: Volume level (0.0 to 1.0). Default is 1.
 */
export const playSound = (url, volume = 1) => {
    try {
      const audio = new Audio(url);
      audio.volume = volume;
      
      // Play the sound
      const playPromise = audio.play();
  
      // Handling browser autoplay policies
      if (playPromise !== undefined) {
        playPromise
          .then(() => {
            // Audio started playing successfully
          })
          .catch((error) => {
            console.error("Audio playback failed:", error);
          });
      }
    } catch (err) {
      console.error("Error initializing audio:", err);
    }
  };