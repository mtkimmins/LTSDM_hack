use a1800_codec::A1800Encoder;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn encode_pcm(pcm: &[i16], bitrate: u16) -> Result<Vec<u8>, JsValue> {
    if pcm.is_empty() {
        return Err(JsValue::from_str("Audio is empty."));
    }

    let mut encoder = A1800Encoder::new(bitrate)
        .map_err(|e| JsValue::from_str(&e.to_string()))?;

    let frame_words = encoder.encoded_frame_size();
    let mut encoded_words = vec![0i16; frame_words];
    let mut frame = [0i16; 320];
    let mut payload = Vec::<u8>::new();

    for chunk in pcm.chunks(320) {
        frame.fill(0);
        frame[..chunk.len()].copy_from_slice(chunk);

        encoder
            .encode_frame(&frame, &mut encoded_words)
            .map_err(|e| JsValue::from_str(&e.to_string()))?;

        for word in &encoded_words {
            payload.extend_from_slice(&word.to_le_bytes());
        }
    }

    let payload_len = u32::try_from(payload.len())
        .map_err(|_| JsValue::from_str("Encoded audio is too large."))?;

    let mut result = Vec::with_capacity(6 + payload.len());
    result.extend_from_slice(&payload_len.to_le_bytes());
    result.extend_from_slice(&bitrate.to_le_bytes());
    result.extend_from_slice(&payload);

    Ok(result)
}
