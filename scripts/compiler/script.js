/*
TODO LIST
- cut out the wasm files I need, delete CARGO src
- write pseudocode for each function
- study required ux of light sequence maker
---
DONE
*/


//////////////////////////////////////////
//  MODULES/IMPORTS
//////////////////////////////////////////
import init, { encode_pcm } from "./a1800-wasm/pkg/a1800_wasm.js"
await init();
/*
// Generate 1 second of synthetic 440 Hz audio at 16 kHz.
const sampleRate = 16000;
const pcm = new Int16Array(sampleRate);

for (let i = 0; i < pcm.length; i++) {
    pcm[i] = Math.round(
        10000 * Math.sin(2 * Math.PI * 440 * i / sampleRate)
    );
}

try {
    const output = encode_pcm(pcm, 16000);

    console.log("Encoding succeeded!");
    console.log("Output type:", output.constructor.name);
    console.log("Total bytes:", output.length);

    const header = new DataView(
        output.buffer,
        output.byteOffset,
        output.byteLength
    );

    const payloadLength = header.getUint32(0, true);
    const bitrate = header.getUint16(4, true);

    console.log("Header payload length:", payloadLength);
    console.log("Bitrate:", bitrate);
    console.log(
        "Header matches output:",
        payloadLength === output.length - 6
    );

    if (
        output.length > 6 &&
        payloadLength === output.length - 6 &&
        bitrate === 16000
    ) {
        console.log("Basic A1800 output checks passed.");
    }
    const blob = new Blob([output], {
    type: "application/octet-stream"
});

const url = URL.createObjectURL(blob);
const link = document.createElement("a");

link.href = url;
link.download = "wasm-test.a18";
link.click();

setTimeout(() => URL.revokeObjectURL(url), 1000);
} catch (error) {
    console.error("Encoding failed:", error);
}
console.log("A1800 initialized");
console.log("Encoder function:", typeof encode_pcm);
*/
//////////////////////////////////////////
//      CONSTANTS/VARS
//////////////////////////////////////////
//CONST
//taskbar stuff
const topTaskbar = document.getElementById("top-taskbar");
const compileLTSDMButton = document.getElementById("compile-ltsdm-button");
const compileSVGButton = document.getElementById("compile-svg-button");
const compilePDFButton = document.getElementById("compile-pdf-button");
//data stuff
const dataContainer = document.getElementById("data-container");
const frame = document.getElementById("frame");

//audio stuff
const uploadAudioButton = document.getElementById("audio-upload-button");

const audioInput = document.getElementById("audio-input");

//image stuff

//summary bar stuff

//VARS
let image_lock = false;







///////////////////////////////////////////
//      EVENT LISTENERS
///////////////////////////////////////////
//compiling
function compileLTSDM(){};
function compileSVG(){};
function compilePDF(){};
function compileFull(){};
function setCompileLocation(){};

//adding and managing audio files
function uploadAudio(){
    audioInput.click();
    //console.log("choosing");
};
async function processAudio(){
    //make sure only 1 file can be selected
    const files = audioInput.files;
    if (files.length>1) return;
    const file = audioInput.files[0];
    if (!file) return;
    //console.log("Got the files");
    const track = await encodeAudio(file);
};

function resetAudio(){};

function playAudio(){};
function resumeAudio(){};
function stopAudio(){};

//managing light data
function selectLightInterval(){};
function moveLightIndicator(){};

function dragProgressBar(){};

function cutAudioSegment(){};
function jumpTime(){};
function assignLightColour(){};

//managing image data
function uploadImage(){};
function toggleImageEdits(){
    image_lock = !image_lock;
};


///////////////////////////////////////////
//      CREATION
///////////////////////////////////////////
function generateFrameElements() {};

function addFrameElements() {};

function initializeLTSDMElements() {};

////////////////////////////////////////////
//      AUDIO CODEC
////////////////////////////////////////////
async function encodeAudio(file){
    if (!file) {
        status.textContent = "Choose a WAV file first.";
        return;
    }

    let audioContext;

    try {
        status.textContent = "Reading and decoding WAV...";

        // Read the selected file locally.
        const arrayBuffer = await file.arrayBuffer();

        // Decode the audio in the browser.
        audioContext = new AudioContext();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

        // Mix all channels into mono.
        const mono = new Float32Array(audioBuffer.length);
        const channels = audioBuffer.numberOfChannels;

        for (let channel = 0; channel < channels; channel++) {
            const samples = audioBuffer.getChannelData(channel);

            for (let i = 0; i < samples.length; i++) {
                mono[i] += samples[i] / channels;
            }
        }

        // Resample to 16 kHz using linear interpolation.
        const targetRate = 16000;
        const outputLength = Math.ceil(
            mono.length * targetRate / audioBuffer.sampleRate
        );

        const pcm = new Int16Array(outputLength);

        for (let i = 0; i < outputLength; i++) {
            const sourcePosition = i * audioBuffer.sampleRate / targetRate;
            const left = Math.floor(sourcePosition);
            const right = Math.min(left + 1, mono.length - 1);
            const fraction = sourcePosition - left;

            const sample =
                mono[left] * (1 - fraction) +
                mono[right] * fraction;

            const clamped = Math.max(-1, Math.min(1, sample));

            pcm[i] = Math.round(
                clamped < 0 ? clamped * 32768 : clamped * 32767
            );
        }

        status.textContent = "Encoding A1800...";

        // Call the WASM encoder you already built.
        const output = encode_pcm(pcm, 16000);

        // Download the resulting .a18 file.
        const blob = new Blob([output], {
            type: "application/octet-stream"
        });

        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");

        link.href = url;
        link.download = file.name.replace(/\.wav$/i, "") + ".a18";
        link.click();

        setTimeout(() => URL.revokeObjectURL(url), 1000);

        const payloadLength = new DataView(
            output.buffer,
            output.byteOffset,
            output.byteLength
        ).getUint32(0, true);

        status.textContent =
            `Encoded ${file.name}: ${pcm.length} PCM samples, ` +
            `${output.length} output bytes, ` +
            `${payloadLength} payload bytes.`;
    } catch (error) {
        console.error(error);
        status.textContent = `Encoding failed: ${error.message}`;
    } finally {
        if (audioContext) {
            await audioContext.close();
        }
    }
};


////////////////////////////////////////////
//      RUNTIME
////////////////////////////////////////////
//Assign the event listeners
uploadAudioButton.addEventListener("click",uploadAudio);
audioInput.addEventListener("change", processAudio);