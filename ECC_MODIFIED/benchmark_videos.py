import base64
from app import VideoSteganography  # app.py must define this

SECRET_VIDEO = r"C:\Users\jyoth\OneDrive\Desktop\PROJECT\video\out_100ms.mp4"
COVER_VIDEO  = r"C:\Users\jyoth\OneDrive\Desktop\PROJECT\video\out_500ms.mp4"

ITER = 3  # fewer runs because video is heavy

def run_tests(curve_name):
    print(f"\nRunning VIDEO tests for {curve_name} ...")
    steg = VideoSteganography(curve_name)

    priv, pub = steg.generate_key_pair()
    pub_bytes = steg.serialize_public_key(pub)
    pub_b64 = base64.b64encode(pub_bytes)

    enc_times = []
    dec_times = []

    for i in range(ITER):
        enc_t = steg.hide_video_in_video(
            COVER_VIDEO,
            SECRET_VIDEO,
            base64.b64decode(pub_b64),
            "tmp_video_stego.mp4",
        )
        enc_times.append(enc_t)

        dec_t = steg.extract_video_from_video(
            "tmp_video_stego.mp4",
            priv,
            "tmp_video_out.mp4",
        )
        dec_times.append(dec_t)

        print(f"  Iter {i+1}: enc={enc_t:.6f}s  dec={dec_t:.6f}s")

    avg_enc = sum(enc_times) / ITER
    avg_dec = sum(dec_times) / ITER
    avg_total = avg_enc + avg_dec

    print(f"\n{curve_name} VIDEO averages over {ITER} runs:")
    print(f"  Avg enc time  : {avg_enc:.6f} s")
    print(f"  Avg dec time  : {avg_dec:.6f} s")
    print(f"  Avg total time: {avg_total:.6f} s")

    return avg_enc, avg_dec, avg_total

if __name__ == "__main__":
    curve_enc, curve_dec, curve_total = run_tests("curve25519")
    secp_enc, secp_dec, secp_total = run_tests("secp256r1")

    print("\n===== FINAL VIDEO SUMMARY (same secret & cover) =====")
    print(f"Curve25519  -> enc={curve_enc:.6f}s  dec={curve_dec:.6f}s  total={curve_total:.6f}s")
    print(f"secp256r1   -> enc={secp_enc:.6f}s  dec={secp_dec:.6f}s  total={secp_total:.6f}s")
