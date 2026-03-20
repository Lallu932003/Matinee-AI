import os
import rembg

paths = [
    r"C:\Users\Ann Mariya Lalu\.gemini\antigravity\brain\068f6077-e7a7-4d46-b0d7-a935de4df7b0\cid_moosa_1773893744898.png",
    r"C:\Users\Ann Mariya Lalu\.gemini\antigravity\brain\068f6077-e7a7-4d46-b0d7-a935de4df7b0\karthumbi_1773893762783.png",
    r"C:\Users\Ann Mariya Lalu\.gemini\antigravity\brain\068f6077-e7a7-4d46-b0d7-a935de4df7b0\dashamoolam_dhamu_1773893782899.png",
    r"C:\Users\Ann Mariya Lalu\.gemini\antigravity\brain\068f6077-e7a7-4d46-b0d7-a935de4df7b0\dude_aadu_1773893801622.png"
]

for cp in paths:
    out_path = cp.replace(".png", "_cutout.png")
    try:
        with open(cp, "rb") as i:
            with open(out_path, "wb") as o:
                input_bytes = i.read()
                output_bytes = rembg.remove(input_bytes)
                o.write(output_bytes)
        print(f"Processed {out_path}")
    except Exception as e:
        print(f"Error processing {cp}: {e}")
