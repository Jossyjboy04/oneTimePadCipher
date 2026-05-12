import streamlit as st
import os

# --- 1. PAGE & STATE CONFIG ---
st.set_page_config(page_title="Digital OTP Lab", page_icon="🔐", layout="centered")

# Memory for automatic syncing between tabs
if 'vault_cipher' not in st.session_state:
    st.session_state.vault_cipher = ""
if 'vault_key' not in st.session_state:
    st.session_state.vault_key = ""

# --- 2. THE BITWISE XOR ENGINE ---

def engine_xor(text, key_string, mode='encrypt'):
    """
    Pure Digital Logic: Bitwise XOR
    Logic: Plaintext Byte XOR Numeric Byte -> Hexadecimal Output
    """
    try:
        # Clean and convert the numeric key string into a list of integers
        # Input format expected: "215, 142"
        k_bytes = [int(x.strip()) for x in key_string.split(",")]
        
        if mode == 'encrypt':
            # Convert string to raw UTF-8 bytes
            t_bytes = text.encode('utf-8')
            
            if len(k_bytes) < len(t_bytes):
                return f"ERROR: Key length ({len(k_bytes)}) is shorter than message ({len(t_bytes)})"
            
            # The XOR operation: t ^ k
            res_bytes = bytes([t ^ k for t, k in zip(t_bytes, k_bytes)])
            
            # Return as Hex for readability (prevents 'unprintable character' crashes)
            return res_bytes.hex().upper()
        
        else: # DECRYPT MODE
            # Convert Hex string back to raw bytes
            c_bytes = bytes.fromhex(text)
            
            if len(k_bytes) < len(c_bytes):
                return "ERROR: Key list is too short for this ciphertext"
            
            # XOR again to reverse (Symmetric property)
            res_bytes = bytes([c ^ k for c, k in zip(c_bytes, k_bytes)])
            
            # Decode back to UTF-8 text
            return res_bytes.decode('utf-8', errors='ignore')
            
    except ValueError:
        return "ERROR: Invalid Key format. Use comma-separated numbers (e.g., 215, 142)"
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🛡️ XOR OTP Console")
    st.write("**Lecturer:** DR. OMODUNBI")
    menu = st.radio("Navigation", [
        "Interface", 
        "The Math (Bitwise)", 
        "Vulnerability Lab", 
        "Engineering Rules", 
        "Test Case"
    ])
    st.divider()
    st.caption("Federal University Oye Ekiti - CPE")

# --- 4. CONTENT ROUTING ---

if menu == "Interface":
    st.header("Digital One-Time Pad")
    st.caption("Protocol: Bitwise XOR (Symmetric)")

    tab1, tab2 = st.tabs(["🔒 ENCRYPT", "🔓 DECRYPT"])

    with tab1:
        msg_in = st.text_area("Plaintext Message:").strip()
        key_in = st.text_input("Secret Key (Numeric Bytes, comma separated):", placeholder="e.g., 215, 142")
        
        if st.button("Generate Ciphertext"):
            if not msg_in or not key_in:
                st.warning("Ensure both Plaintext and Key fields are filled.")
            else:
                result = engine_xor(msg_in, key_in, 'encrypt')
                if "ERROR" in result:
                    st.error(result)
                else:
                    st.session_state.vault_cipher = result
                    st.session_state.vault_key = key_in
                    st.success(f"**Hex Ciphertext:** `{result}`")

    with tab2:
        c_field = st.text_area("Hex Ciphertext:", value=st.session_state.vault_cipher)
        k_field = st.text_input("Key Used:", value=st.session_state.vault_key)
        
        if st.button("Run Decryption"):
            decoded = engine_xor(c_field, k_field, 'decrypt')
            if "ERROR" in decoded:
                st.error(decoded)
            else:
                st.markdown("### Decrypted Message:")
                st.success(f"**{decoded}**")

elif menu == "The Math (Bitwise)":
    st.header("The Digital Logic")
    st.write("XOR is a bitwise operator. It follows a simple rule for every bit:")
    
    # Truth Table
    st.table({
        "Bit A": [0, 0, 1, 1],
        "Bit B": [0, 1, 0, 1],
        "Result (A ⊕ B)": [0, 1, 1, 0]
    })
    
    st.write("Mathematically, XOR is **Binary Addition without Carry**. It is preferred in engineering because it is extremely fast and self-inverting.")

elif menu == "Vulnerability Lab":
    st.header("The Two-Time Pad Attack")
    st.error("Key reuse collapses the security of the XOR OTP.")
    st.write("If you use Key $K$ for Message $A$ and Message $B$:")
    st.latex(r"(A \oplus K) \oplus (B \oplus K) = A \oplus B")
    st.info("The key cancels itself out. An attacker only needs the XOR sum of the two messages to start frequency analysis.")

elif menu == "Engineering Rules":
    st.header("Golden Rules for CPE")
    st.markdown("""
    1. **Key Length:** Key bytes must be $\geq$ Message bytes.
    2. **True Randomness:** The numeric key must be generated via a non-deterministic source.
    3. **Uniqueness:** A key is spent after one XOR operation.
    4. **Storage:** Ciphertext is Hex-encoded to maintain data integrity across different systems.
    """)

elif menu == "Test Case":
    st.header("Validation Proof")
    st.write("To verify the code, use the following vector:")
    st.markdown("""
    - **Message:** `OK`
    - **Key:** `215, 142`
    - **Logic:** - 'O' (79) $\oplus$ 215 = 159 (**9F**)
        - 'K' (75) $\oplus$ 142 = 199 (**C7**)
    - **Expected Result:** `9FC7`
    """)