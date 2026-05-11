import streamlit as st

# --- 1. PAGE & STATE CONFIG ---
st.set_page_config(page_title="OTP Hybrid Studio", page_icon="🛡️", layout="centered")

# Memory for automatic syncing between tabs
if 'vault_cipher' not in st.session_state:
    st.session_state.vault_cipher = ""
if 'vault_key' not in st.session_state:
    st.session_state.vault_key = ""

# --- 2. THE CRYPTO ENGINES ---

def engine_modular(text, key, mode='encrypt'):
    """Classical Logic: (Letter Position + Letter Position) MOD 26"""
    text = "".join(filter(str.isalpha, text.upper()))
    key = "".join(filter(str.isalpha, key.upper()))
    res = ""
    for t, k in zip(text, key):
        t_val = ord(t) - ord('A')
        k_val = ord(k) - ord('A')
        val = (t_val + k_val) % 26 if mode == 'encrypt' else (t_val - k_val + 26) % 26
        res += chr(val + ord('A'))
    return res

def engine_xor(text, key_string, mode='encrypt'):
    """Modern Logic: (ASCII Byte XOR Numeric Byte) -> Hex"""
    try:
        # Convert comma-separated string "215, 142" into integers
        k_bytes = [int(x.strip()) for x in key_string.split(",")]
        
        if mode == 'encrypt':
            t_bytes = text.encode('utf-8')
            if len(k_bytes) < len(t_bytes):
                return "ERROR: Key list too short"
            res_bytes = bytes([t ^ k for t, k in zip(t_bytes, k_bytes)])
            return res_bytes.hex().upper()
        else:
            c_bytes = bytes.fromhex(text)
            if len(k_bytes) < len(c_bytes):
                return "ERROR: Key list too short"
            res_bytes = bytes([c ^ k for c, k in zip(c_bytes, k_bytes)])
            return res_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🔐 OTP Control")
    menu = st.radio("Features", [
        "App Interface", 
        "How It Works (Logic)", 
        "Encryption Rules", 
        "The Attack Lab", 
        "Tips", 
        "Example"
    ])
    st.divider()
    logic_choice = st.selectbox("Select Protocol:", ["Letter-based (Modular)", "Modern (XOR)"])

# --- 4. CONTENT ROUTING ---

if menu == "App Interface":
    st.header(f"One-Time Pad Interface")
    st.caption(f"Protocol: {logic_choice}")

    tab1, tab2 = st.tabs(["🔒 ENCRYPT", "🔓 DECRYPT"])

    with tab1:
        msg_in = st.text_area("Plaintext Message:").strip()
        if logic_choice == "Modern (XOR)":
            k_label = "Secret Key (Numeric Bytes, comma separated):"
            k_placeholder = "e.g., 215, 142"
        else:
            k_label = "Secret Key (Letters):"
            k_placeholder = "e.g., SECRET"
            
        key_in = st.text_input(k_label, placeholder=k_placeholder)
        
        if st.button("Run Encryption"):
            if not msg_in or not key_in:
                st.warning("Please fill in both fields.")
            else:
                result = engine_modular(msg_in, key_in, 'encrypt') if logic_choice == "Letter-based (Modular)" else engine_xor(msg_in, key_in, 'encrypt')
                
                if "ERROR" in result:
                    st.error(result)
                else:
                    st.session_state.vault_cipher = result
                    st.session_state.vault_key = key_in
                    st.success(f"**Result:** `{result}`")

    with tab2:
        c_field = st.text_area("Ciphertext:", value=st.session_state.vault_cipher)
        k_field = st.text_input("Key Used:", value=st.session_state.vault_key)
        
        if st.button("Run Decryption"):
            decoded = engine_modular(c_field, k_field, 'decrypt') if logic_choice == "Letter-based (Modular)" else engine_xor(c_field, k_field, 'decrypt')
            st.markdown("### Decrypted Message:")
            st.success(f"**{decoded}**")

elif menu == "How It Works (Logic)":
    st.header("The Mathematical Logic")
    if logic_choice == "Letter-based (Modular)":
        st.subheader("Modulo 26 Arithmetic")
        st.write("Treats the alphabet as a cycle. We add the positions of message and key letters.")
        st.latex(r"Cipher = (Message + Key) \pmod{26}")
    else:
        st.subheader("Bitwise XOR (Numeric)")
        st.write("Converts characters to ASCII(American Standard Code for Information Interchange), then XORs with numeric bytes. This is binary-level security.")
        st.latex(r"Plain \oplus Key = Cipher")

elif menu == "Encryption Rules":
    st.header("The Golden Rules")
    st.markdown("""
    1. **Key Length:** Key must be $\geq$ Message.
    2. **Randomness:** The key must be a non-repeating string of random noise.
    3. **One-Time Use:** Never reuse a key. If used twice, the cipher is broken.
    4. **Destruction:** Delete the key immediately after use.
    """)

elif menu == "The Attack Lab":
    st.header("The Two-Time Pad Attack")
    st.error("Reusing a key is the only way to crack a One-Time Pad.")
    st.write("If Key $K$ is used for two messages ($M_1, M_2$):")
    st.latex(r"C_1 \oplus C_2 = (M_1 \oplus K) \oplus (M_2 \oplus K) = M_1 \oplus M_2")
    st.write("""
    An attacker can XOR the two ciphertexts to eliminate the key. 
    By applying 'Crib Dragging' (testing common words like 'THE'), they can recover both original messages.
    """)

elif menu == "Tips":
    st.header("Engineer's Field Notes")
    st.info("💡 **Digital vs. Manual:** XOR is the industry standard for software. Modular is for human-to-human spycraft.")
    st.info("💡 **Why Hex?** Results like '9F' aren't letters—they are raw byte values. Hex makes them readable.")
    st.info("💡 **Key Sync:** In this app, we use 'Session State' to simulate passing a secret note between tabs.")

elif menu == "Example":
    st.header("Validation Walkthrough")
    st.subheader("XOR Numeric Mode")
    st.write("Message: **OK** | Key: **215, 142**")
    st.markdown("""
    - **O** (79) $\oplus$ **215** = **159** (Hex: **9F**)
    - **K** (75) $\oplus$ **142** = **199** (Hex: **C7**)
    - **Result:** `9FC7`
    """)