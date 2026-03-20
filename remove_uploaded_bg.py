import os
import rembg

paths = [
    r"C:\Users\Ann Mariya Lalu\.gemini\antigravity\brain\068f6077-e7a7-4d46-b0d7-a935de4df7b0\media__1773894459941.png",
    r"C:\Users\Ann Mariya Lalu\.gemini\antigravity\brain\068f6077-e7a7-4d46-b0d7-a935de4df7b0\media__1773894540747.png",
    r"C:\Users\Ann Mariya Lalu\.gemini\antigravity\brain\068f6077-e7a7-4d46-b0d7-a935de4df7b0\media__1773894573983.png",
    r"C:\Users\Ann Mariya Lalu\.gemini\antigravity\brain\068f6077-e7a7-4d46-b0d7-a935de4df7b0\media__1773894610131.png"
]

for cp in paths:
    out_path = cp.replace(".png", "_cutout.png")
    try:
        with open(cp, "rb") as i:
            with open(out_path, "wb") as o:
                output_bytes = rembg.remove(i.read())
                o.write(output_bytes)
        print(f"Processed {out_path}")
    except Exception as e:
        print(f"Error processing {cp}: {e}")
