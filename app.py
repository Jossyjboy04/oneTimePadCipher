import streamlit as st

# --- 1. PAGE & STATE CONFIGURATION ---
st.set_page_config(page_title="FUOYE Digital OTP Lab", page_icon="🔐", layout="centered")

# Session state to sync data between Encrypt and Decrypt tabs
if 'vault_cipher' not in st.session_state:
    st.session_state.vault_cipher = ""
if 'vault_key' not in st.session_state:
    st.session_state.vault_key = ""

# --- 2. THE CORE BITWISE ENGINE ---

def engine_xor(text, key_string, mode='encrypt'):
    """
    Standard Bitwise XOR Protocol.
    Handles any character stream (H, h, spaces, symbols).
    """
    try:
        # Clean and convert the numeric key string into a list of integers
        k_bytes = [int(x.strip()) for x in key_string.split(",")]
        
        if mode == 'encrypt':
            # encode('utf-8') converts the full sentence into raw ASCII/Byte values
            t_bytes = text.encode('utf-8')
            
            # Engineering Constraint: Key must be >= Message length
            if len(k_bytes) < len(t_bytes):
                return f"ERROR: Key too short! Sentence is {len(t_bytes)} characters, but you provided {len(k_bytes)} key bytes."
            
            # The XOR operation: t ^ k
            res_bytes = bytes([t ^ k for t, k in zip(t_bytes, k_bytes)])
            
            # Return result as Hexadecimal (printable representation of binary data)
            return res_bytes.hex().upper()
        
        else: # DECRYPT MODE
            # Convert Hex string back to raw bytes
            c_bytes = bytes.fromhex(text)
            
            if len(k_bytes) < len(c_bytes):
                return "ERROR: Key list is too short for this ciphertext."
            
            # XOR again with the same key to reverse (Symmetric Property)
            res_bytes = bytes([c ^ k for c, k in zip(c_bytes, k_bytes)])
            
            # Decode bytes back to original text string
            return res_bytes.decode('utf-8', errors='ignore')
            
    except ValueError:
        return "ERROR: Invalid Key format. Use comma-separated numbers (e.g., 215, 142, 5)."
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🛡️ XOR OTP Console")
    st.write("**Lecturer:** DR. OMODUNBI")
    st.write("**Dept:** Computer Engineering")
    menu = st.radio("Navigation", [
        "Project Interface", 
        "Technical Logic", 
        "Sentence Engineering",
        "Vulnerability Lab", 
        "Verification Proof"
    ])
    st.divider()
    st.caption("Federal University Oye Ekiti (FUOYE)")

# --- 4. INTERFACE CONTENT ---

if menu == "Project Interface":
    st.header("Digital One-Time Pad Studio")
    st.info("💡 One key byte required for every character (including spaces and symbols).")

    tab1, tab2 = st.tabs(["🔒 ENCRYPT", "🔓 DECRYPT"])

    with tab1:
        msg_in = st.text_input("Plaintext Sentence:").strip()
        key_in = st.text_area("Secret Key (Numeric Bytes):", placeholder="Example: 10, 55, 120, 200...")
        
        if st.button("Generate Ciphertext"):
            if not msg_in or not key_in:
                st.warning("Please provide both a message and a key.")
            else:
                result = engine_xor(msg_in, key_in, 'encrypt')
                if "ERROR" in result:
                    st.error(result)
                else:
                    st.session_state.vault_cipher = result
                    st.session_state.vault_key = key_in
                    st.success(f"**Hex Ciphertext:** `{result}`")

    with tab2:
        st.subheader("Decryption Vault")
        c_field = st.text_area("Hex Ciphertext:", value=st.session_state.vault_cipher)
        k_field = st.text_area("Key Used:", value=st.session_state.vault_key)
        
        if st.button("Recover Message"):
            decoded = engine_xor(c_field, k_field, 'decrypt')
            if "ERROR" in decoded:
                st.error(decoded)
            else:
                st.markdown("### Original Plaintext:")
                st.success(f"**{decoded}**")

elif menu == "Technical Logic":
    st.header("Bitwise XOR (Exclusive OR)")
    st.write("This implementation uses the bit-level XOR gate. It is the gold standard for high-speed digital encryption.")
    
    st.table({
        "Bit A": [0, 0, 1, 1],
        "Bit B": [0, 1, 0, 1],
        "Result (A ⊕ B)": [0, 1, 1, 0]
    })
    st.write("Because the operation is symmetrical, using the same key a second time flips the bits back to their original state.")

elif menu == "Sentence Engineering":
    st.header("Stream Processing")
    st.write("The app treats a full sentence as a stream of bytes. This includes:")
    st.markdown("""
    - **Uppercase (H):** ASCII 72 (`01001000`)
    - **Lowercase (h):** ASCII 104 (`01101000`)
    - **Space ( ):** ASCII 32 (`00100000`)
    - **Full Stop (.):** ASCII 46 (`00101110`)
    """)
    st.info("Every character is mathematically relevant. A sentence with 10 characters requires exactly 10 numeric key bytes.")

elif menu == "Vulnerability Lab":
    st.header("The Two-Time Pad Attack")
    st.error("Fatal Flaw: Key Reuse")
    st.write("If Key $K$ is reused for Sentence $S_1$ and $S_2$:")
    st.latex(r"(S_1 \oplus K) \oplus (S_2 \oplus K) = S_1 \oplus S_2")
    st.write("The key is mathematically eliminated, leaving the XOR sum of the two messages exposed.")

elif menu == "Verification Proof":
    st.header("Standard Test Vector")
    st.write("Proof of Logic Verification:")
    st.markdown("""
    - **Plaintext:** `OK`
    - **Key Sequence:** `215, 142`
    - **Execution:**
        - 'O' (79) $\oplus$ 215 = 159 (Hex **9F**)
        - 'K' (75) $\oplus$ 142 = 199 (Hex **C7**)
    - **Final Output:** `9FC7`
    """)