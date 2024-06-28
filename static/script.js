window.onSpotifyWebPlaybackSDKReady = () => {
    const token = "your_access_token";
    const player = new Spotify.Player({
      name: "My Spotify Player",
      getOAuthToken: (cb) => {
        cb(token);
      },
    });
  
    // Add event listeners and control the player
    player.addListener("ready", ({ device_id }) => {
      console.log("The Spotify player is ready to play music!");
      // ...
    });
  
    player.connect();
  };
  