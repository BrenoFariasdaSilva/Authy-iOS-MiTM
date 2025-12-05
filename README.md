<div align="center">

# [Authy-iOS-MiTM.](https://github.com/BrenoFariasdaSilva/Authy-iOS-MiTM) <img src="https://raw.githubusercontent.com/github/explore/main/topics/authentication/authentication.png"  width="3%" height="3%">

</div>

<div align="center">

---

Guide to extract Authenticator Tokens (TOTP URI) from the [Authy iOS App](https://apps.apple.com/br/app/twilio-authy/id494168017) with [MITMProxy](https://www.mitmproxy.org/).

This is an improved and fully automated, documented, improved, and easy to use version of the original repository created by [AlexTech01](https://github.com/AlexTech01).

In this fork, I've modified the original scripts to be more user-friendly, including documentation, virtual environment setup, `requirements.txt`, `.env`, `.gitignore`, and a `Makefile` for easy setup and usage. Not only that, for the files `decrypt.py`, I've improved the code quality, readability, and split big functions into smaller ones for better maintainability. Also, the original `script.py` was broken in the QR code generation, so I fixed it, splitting the `script.py` into two files: `generate_uris.py` for the URI generation and `generate_qr_codes.py` for the QR code generation. The original script to generate QR Codes was also more complex and used the pillow lib. I rewrote the code to be simpler and more efficient. There was also the addition of the `main.py` file, which is the main entry point of the script, and it will call all of the three scripts (`authenticador_tokens.py`, `generate_uris.py`, and `generate_qr_codes.py`) to make it easier to use. Not only that, but I've added the `Proton Authenticator` support, which a few people asked for. Lastly, I've updated this README file to include all of the new features and improvements made in this fork. With all that said, this is an improvement over the original project, which was already a great project, and it is now easier to use and more user-friendly, but obviously the original authors deserve all the credit, as I would not be able to do this without their work.

It took a lot of work to make this fork, so I hope you enjoy it and find it useful. If you have any questions or suggestions, feel free to open an issue or a pull request.

---

</div>

<div align="center">

![GitHub Code Size in Bytes Badge](https://img.shields.io/github/languages/code-size/BrenoFariasdaSilva/Authy-iOS-MiTM)
![GitHub Last Commit Badge](https://img.shields.io/github/last-commit/BrenoFariasdaSilva/Authy-iOS-MiTM)
![GitHub License Badge](https://img.shields.io/github/license/BrenoFariasdaSilva/Authy-iOS-MiTM)
![Wakatime Badge](https://wakatime.com/badge/github/BrenoFariasdaSilva/Authy-iOS-MiTM.svg)

</div>

<div align="center">

![RepoBeats Statistics](https://repobeats.axiom.co/api/embed/acb10c4d8be1329bb6b375f5170d258cc275e940.svg "Repobeats analytics image")

</div>

## Table of Contents
- [Authy-iOS-MiTM. ](#authy-ios-mitm-)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Requirements](#requirements)
  - [Repository Setup](#repository-setup)
    - [1. Install Python](#1-install-python)
      - [Linux](#linux)
      - [macOS](#macos)
      - [Windows](#windows)
    - [2. Install `make` utility](#2-install-make-utility)
      - [Linux](#linux-1)
      - [macOS](#macos-1)
      - [Windows](#windows-1)
    - [3. Clone the repository](#3-clone-the-repository)
    - [4. Virtual environment (Strongly Recommended)](#4-virtual-environment-strongly-recommended)
    - [5. Install dependencies](#5-install-dependencies)
  - [Setting up and Using the Project](#setting-up-and-using-the-project)
    - [Step 1: Setting up mitmproxy](#step-1-setting-up-mitmproxy)
      - [Installing the mitmproxy root certificate on iOS](#installing-the-mitmproxy-root-certificate-on-ios)
    - [Troubleshooting / Alternative Method](#troubleshooting--alternative-method)
    - [Step 2: Dumping tokens](#step-2-dumping-tokens)
      - [How to find the correct packet in mitmweb](#how-to-find-the-correct-packet-in-mitmweb)
    - [Step 3: Setting Up Requirements](#step-3-setting-up-requirements)
    - [Step 4: Decrypting tokens](#step-4-decrypting-tokens)
    - [Proton Authenticator support](#proton-authenticator-support)
  - [Troubleshooting / Alternative Method](#troubleshooting--alternative-method-1)
    - [QR Generation Issues on Windows](#qr-generation-issues-on-windows)
    - [About `URIs.json`](#about-urisjson)
    - [Cleaning the Project](#cleaning-the-project)
  - [Compatibility note](#compatibility-note)
  - [Other info](#other-info)
  - [Contributing](#contributing)
  - [License](#license)
    - [MIT License](#mit-license)

## Introduction

This repository provides a guide and scripts to extract authenticator tokens from the [Authy iOS App](https://apps.apple.com/br/app/twilio-authy/id494168017) using [**MITMProxy** (Man-in-the-Middle proxy)](https://www.mitmproxy.org/). [Authy](https://apps.apple.com/br/app/twilio-authy/id494168017) is a popular two-factor authentication (2FA) app that provides an additional layer of security for your online accounts. However, it does not provide a built-in way to export or backup your tokens. Also, since the [Authy Desktop App was discontinued](https://help.twilio.com/articles/22771146070299-User-guide-End-of-Life-EOL-for-Twilio-Authy-Desktop-app), exporting tokens from the Authy Desktop App is no longer an option.  
So, by using MITMProxy, it enables you to capture HTTPS traffic, extract encrypted tokens, and decrypt them to obtain authenticator seeds.
In a short way, you install MITMProxy, set manually the proxy on your iOS device to be the MITMProxy installed on your computer, so, when you log-out and log back in, as your computer is the proxy for your iOS device, it will capture the HTTPS traffic from the Authy app, which contains your authenticator tokens file (`authenticator_tokens.json`) in encrypted form. After that, you can decrypt the tokens using a Python script and your backup password, which will give you access to your authenticator Time-based One-Time Password (TOTP) Uniform Resource Identifier (URI) for many Authenticator apps, such as [2FA](https://apps.apple.com/us/app/2fa-authenticator-2fas/id1217793794), [Aegis](https://getaegis.app/), [Google Authenticator](https://apps.apple.com/us/app/google-authenticator/id388497605), and [Microsoft Authenticator](https://www.microsoft.com/en/security/mobile-authenticator-app). With those URIs, you can import your tokens into any of those apps, or scan the generated QR codes for them. **Proton Authenticator** is now supported, but it requires a special JSON format for import, which is automatically generated as `proton_authenticator.json` by the script. See below for details.

> [!NOTE]
> You can also store the TOTP URIs in a password manager that supports TOTP, such as [Bitwarden](https://bitwarden.com/help/integrated-authenticator/). BitWarden, inside each login, there is a field below the password field called "Authenticator Key (TOTP)", where you can paste the TOTP URI, and BitWarden will automatically generate the TOTP codes for you. Unfortunately, to actually view the 30-second codes, you need a BitWarden Premium subscription, but this is a good option to store your TOTP URIs securely for backup purposes, rather than storing them in a text file or a JSON file, which is not secure.
>
> Honestly, I would recommend you store the TOTP URIs in Bitwarden and then export the Bitwarden vault periodically as a backup and import it into the Apple's Passwords app, as it will detect the TOTP URIs and generate the TOTP codes for you, so you can use the Passwords app as your main authenticator app. This way, you can have a secure backup of your TOTP URIs and also use them in the Passwords app, which I'm pretty sure is built-in in iOS and MacOS for a few years now and is completely free to use.

---

## Requirements

- A computer (Windows/Mac/Linux)
- An iOS/iPadOS device (using a secondary device is recommended)
- A basic understanding of the command line and running Python scripts
- [mitmproxy](https://www.mitmproxy.org) installed on your computer
- [Python 3.13.1+](https://www.python.org) installed on your computer
- [Make](https://www.gnu.org/software/make/) installed on your computer (optional, but strongly recommended to simplify setup and usage)
- **Windows-specific:** Microsoft Visual C++ Build Tools (part of "Build Tools for Visual Studio") — required by some Python packages that need compilation.

---

## Repository Setup

Before running the project, ensure that both **Python** and the **make utility** are installed on your system. Follow the instructions below according to your operating system.

### 1. Install Python

The project requires **Python 3.9 or higher**.

#### Linux
On Debian/Ubuntu-based distributions:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip -y
```

On Fedora/RHEL-based distributions:

```bash
sudo dnf install python3 python3-venv python3-pip -y
```

Verify installation:

```bash
python3 --version
```

#### macOS
1. Install via Homebrew (recommended):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" # if Homebrew not installed
brew install python
```

2. Verify installation:

```bash
python3 --version
```

#### Windows
1. Download Python from the official website: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
2. Run the installer and check **“Add Python to PATH”**.
3. Verify installation:

```powershell
python --version
```

---

### 2. Install `make` utility

The `make` utility is used to automate tasks such as setting up the virtual environment and installing dependencies.

#### Linux
`make` is usually pre-installed. If not:

```bash
sudo apt install build-essential -y  # Debian/Ubuntu
sudo dnf install make -y            # Fedora/RHEL
make --version
```

#### macOS
`make` comes pre-installed with Xcode Command Line Tools:

```bash
xcode-select --install
make --version
```

#### Windows
1. Install via [Chocolatey](https://chocolatey.org/):

```powershell
choco install make
```

Or, install [GnuWin32 Make](http://gnuwin32.sourceforge.net/packages/make.htm).

2. Verify installation:

```powershell
make --version
```

---

### 3. Clone the repository

1. Clone the repository with the following command:

   ```bash
   git clone https://github.com/BrenoFariasDaSilva/Authy-iOS-MiTM.git
   cd Authy-iOS-MiTM
   ```

### 4. Virtual environment (Strongly Recommended)

With `make`:

```bash
make venv
source venv/bin/activate # Linux/macOS
venv\Scripts\activate # Windows
```

Or manually:

```bash
python -m venv venv
source venv/bin/activate # Linux/macOS
venv\Scripts\activate # Windows
```

### 5. Install dependencies

1. Install Python packages:

With `make`:

```bash
make dependencies
```

Or manually:

```bash
pip install -r requirements.txt
```

---

## Setting up and Using the Project

### Step 1: Setting up mitmproxy

Extracting tokens works by capturing HTTPS traffic received by the Authy app after logging in. This traffic contains your tokens in encrypted form, which is then decrypted in a later step so that you can access your authenticator seeds. In order to receive this traffic, we use mitmproxy, which is an easy-to-use tool that allows you to intercept traffic from apps and websites on your device.

To begin, install [mitmproxy](https://www.mitmproxy.org) on your computer, then run:

```bash
mitmweb --allow-hosts "api.authy.com"
```

in your terminal to launch mitmweb (which is a user-friendly interface for mitmproxy) with HTTPS proxying on for `api.authy.com`. Once proxying has started, connect your iOS device to the proxy:

**On iOS:**  
Settings → Wi-Fi → (your network) → Configure Proxy → set to "Manual"  
Enter your computer's private IP for "Server" and 8080 for "Port".

> [!NOTE]
> Your computer's private IP can be found in its Wi-Fi/network settings, and is typically in the format 192.168.x.x or 10.x.x.x.

---

#### Installing the mitmproxy root certificate on iOS

Once your iOS device is connected to the proxy, you must install the mitmproxy root CA certificate. This is required for HTTPS proxying.  
The root CA keys mitmproxy uses are randomly generated for each installation and are not shared.

1. On your iOS device (with the proxy connected), open Safari and visit:  
  `mitm.it`
2. Under the **iOS** section, tap **"Get mitmproxy-ca-cert.pem"**.
3. Tap **Allow** on the iOS message asking to download a configuration profile.

At this point, the profile is downloaded but **not yet installed**.

4. Go to:  
  **Settings → General → VPN & Device Management**  
  Inside this menu, you will see the downloaded "mitmproxy" profile.  
  Tap it, then tap **Install** (top right corner), and confirm when prompted.

5. **Only after installing the profile**, go to:  
  **Settings → General → About → Certificate Trust Settings**  
  Find **mitmproxy** in the list and toggle **"Enable Full Trust for Root Certificates"** to ON.

---

**Important:** Failure to install the profile via **VPN & Device Management** and then enable full trust in **Certificate Trust Settings** will cause Authy to fail with an SSL validation error.

At this point, you have completed the process of setting up mitmproxy to capture HTTPS traffic from your iOS device. Keep the proxy connected for the next step, which is dumping tokens received from the Authy iOS app.

### Troubleshooting / Alternative Method

Some users reported issues where mitmproxy didn’t capture traffic correctly, or where Authy failed with integrity/SSL errors.  
If you face this, try the following sequence (thanks to **fpwex9** for sharing a working setup on macOS + iOS in [here]( https://gist.github.com/gboudreau/94bb0c11a6209c82418d01a59d958c93?permalink_comment_id=5761814#gistcomment-5761814)):

**1. File descriptor limit (macOS only)**  
If mitmproxy complains about “too many open files”, increase the limit before starting it:

```bash
sudo launchctl limit maxfiles 65536 200000
ulimit -n 65536
```

**2. Start mitmproxy with limited interception (Command 1):**

```bash
mitmweb --allow-hosts "api.authy.com"
```

At this stage, you should be able to open the Authy client, enter your phone number, and send the confirmation request to your second device. The Flow List may still be empty at this point.

**3. Switch to full interception (Command 2):**

```bash
mitmweb --listen-host 0.0.0.0 --listen-port 8080
```

Starting directly with this command may cause an “Integrity check” error in Authy.  
Instead, use this sequence:

- Start with **Command 1**.  
- Launch Authy, enter your phone number, and send the confirmation request.  
- **Before confirming on the second device**, stop mitmproxy and restart it with **Command 2**.  
- Confirm on the second device.  
- Authy should authorize successfully, and mitmproxy will capture the required data.

💡 Tip: You may need to retry 2–3 times with slightly different timing before it works. Be patient.

---

### Step 2: Dumping tokens

> [!NOTE]
> In order for this to work, you must have your Authy tokens synced to the cloud and you must have a backup password set. It is recommended to dump tokens with a secondary device in case something goes wrong.

> [!WARNING]
> If you're only using Authy on a single device, don't forget to [enable Authy multi-device](https://help.twilio.com/articles/19753646900379-Enable-or-Disable-Authy-Multi-Device) before logging out. If you don't, you won't be able to log back into your account and you will have to wait 24 hours for Twilio to recover it.

The first step in dumping tokens is to sign out of the Authy app on your device. Unfortunately, Twilio did not implement a "sign out" feature in the app, so you must delete and reinstall the Authy app from the App Store if you are already signed in. With the proxy connected, sign back in to the app normally (enter your phone number and then authenticate via SMS/phone call/existing device), and then stop once the app asks you for your backup password.

> [!NOTE]
> If you get an "attestation token" error, try opening the Authy app with the proxy disconnected, enter your phone number, and then connect to the proxy before you tap on SMS/phone call/existing device verification.

At this point, mitmproxy should have captured your authenticator tokens in encrypted form.

#### How to find the correct packet in mitmweb

In the mitmweb UI, it’s common to see **many** smaller packets — often POST requests — each containing only a single token.  
These are **not** the ones you want. The correct request contains **all tokens together** in a single response.

1. In the **Flow List** tab, use the search box to look for `"token"`.
2. Among the results, locate the first **GET** request (not POST).
3. Look at the **Size** column — the correct packet will be noticeably larger than the others (typically a few KB if you have many tokens).
4. Open this GET request and check its **Response**; it should look similar to:

  ```json
  {
    "authenticator_tokens": [
     {
      "account_type": "example",
      "digits": 6,
      "encrypted_seed": "something",
      "issuer": "Example.com",
      "key_derivation_iterations": 100000,
      "logo": "example",
      "name": "Example.com",
      "original_name": "Example.com",
      "password_timestamp": 12345678,
      "salt": "something",
      "unique_id": "123456",
      "unique_iv": null
     },
     ...
    ]
  }
  ```

💡 Tip: The right packet is usually one large GET request of 5–10 KB or more, depending on how many tokens you have.

Once found, switch to the Flow tab in mitmweb and click Download to save it as authenticator_tokens.  
We strongly recommend renaming this file to authenticator_tokens.json, but if you don’t, the script will automatically detect it and add the .json extension as needed, but this is not recommended as it may cause unknown issues.

After that, disconnect your device from the proxy (select "Off" in Settings → Wi-Fi → (your network) → Configure Proxy) before exiting mitmweb (Ctrl+C in the terminal) and continuing to the next step.

### Step 3: Setting Up Requirements

Before decrypting your tokens, you need install all of the other requirements. 
First, you must ensure you have [Python 3.13.1+](https://www.python.org) installed on your computer. After that, verify that you have `Make` installed on your computer (it comes pre-installed on Linux and Mac, but Windows users can install it via [Chocolatey](https://chocolatey.org/install) with `choco install make`), then run `make dependencies` to set up a Python virtual environment and install the required dependencies. If you don't have `Make` installed, you can manually set up a Python virtual environment and install the dependencies by following these steps:
1. Open your terminal and navigate to the repository folder.
2. Create a virtual environment by running `python -m venv venv` (or `python3 -m venv venv` depending on your system).
3. Activate the virtual environment:
  - On Windows, run `venv\Scripts\activate`
  - On Mac/Linux, run `source venv/bin/activate`
4. Install the required dependencies by running `pip install -r requirements.txt`

After that, inside the repository folder, copy the `.env-example` file to a new file named `.env` and open it in a text editor. Replace `YOUR_AUTHY_BACKUP_PASSWORD_HERE` with your actual Authy backup password, then save and close the file.

### Step 4: Decrypting tokens

Assuming you i've installed all of the requirements in the previous step, you can now decrypt your tokens.
Inside the repository folder, ensure you have the `authenticator_tokens.json` file you downloaded in Step 2 is in the same folder as the scripts (i.e., the root of the repository, `Authy-iOS-MiTM`). After that, run `make`, which will run the `main.py` script that will call all of the three scripts (`authenticador_tokens.py`, `generate_uris.py`, and `generate_qr_codes.py`) to decrypt your tokens, generate URIs for them (saved in the `URIs.txt` and `URIs.json` files), and optionally generate QR codes for them.

The script will prompt you for your backup password if you didn't create the `.env` file, which does not show in the terminal for privacy reasons. After entering your password and hitting Enter, you should have a `decrypted_tokens.json` file, which contains the decrypted authenticator seeds from your Authy account. Please note that this JSON file is not in a standard format that you can import to other authenticator apps. The file that you can import to other authenticator apps is the `URIs.json` file, which contains the URIs for each of your tokens in a format that is compatible with the authenticator app that you choose during the `generate_uris.py` script execution (`Select an authenticator app to generate URIs for: (1. 2FA, 2. Aegis, 3. Google Authenticator, 4. Microsoft Authenticator, 5. Proton Authenticator`).

### Proton Authenticator support

**Proton Authenticator** requires a specific JSON format for bulk import, which is different from the standard `URIs.json` file. When you select Proton Authenticator in the script, it will generate a file named `proton_authenticator.json` with the required format:

```json
{
  "version": 1,
  "entries": [
    {
      "id": "...",
      "content": {
        "uri": "otpauth://totp/Adobe?secret=...&digits=6&algorithm=SHA1&period=30&issuer=",
        "entry_type": "Totp",
        "name": "Adobe"
      },
      "note": null
    },
    ...
  ]
}
```

This file can be imported directly into Proton Authenticator. The script will automatically create this file for you if you select Proton Authenticator as your target app. Other apps use the standard `URIs.json` and `URIs.txt` files.

> [!NOTE]
> If you see "Decryption failed: Invalid padding length" as the decrypted_seed in your JSON file, you entered an incorrect backup password. Run the script again with the correct backup password.

---

## Troubleshooting / Alternative Method

### QR Generation Issues on Windows

Some users have reported that generated QR files may:
- Use incorrect extensions (e.g., `.wav` instead of `.png`);
- Contain invalid filenames or fail to save properly.

To resolve or prevent these issues:

1. Ensure `Pillow` and `qrcode` were installed successfully inside the virtual environment.
2. Avoid special or reserved Windows filenames (e.g., `CON`, `PRN`, `AUX`, etc.).
3. If encoding issues persist, try running the QR generation script from a **POSIX-like environment** such as:
  - **WSL (Windows Subsystem for Linux)**
  - **Git Bash**
  - **macOS/Linux**
4. As a fallback, use the `URIs.json` file — it contains all **otpauth URIs** your authenticator app can import directly.
  - Most apps (Google Authenticator, Authy, Bitwarden, etc.) support importing from URIs.
  - Alternatively, use an external QR generator that accepts **otpauth URIs**.

---

### About `URIs.json`

The `URIs.json` file serves as a direct backup of all generated **TOTP URIs**.  
If QR generation fails, you can still:

- Import `URIs.json` directly into your preferred authenticator app; or  
- Use an online/offline QR generator that accepts **otpauth://** URIs to recreate the QR codes.

---

### Cleaning the Project

If you encounter environment or dependency issues, you can safely clean and rebuild everything:

```bash
# Remove the virtual environment and temporary files (PowerShell)
Remove-Item -Recurse -Force .\venv
Get-ChildItem -Recurse -Filter *.pyc | Remove-Item -Force
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force

# Recreate the environment
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

This ensures a clean setup equivalent to running `make clean && make`.

## Compatibility note

This method will never work on unrooted Android devices due to the fact that the Authy app only trusts root certificates from the system store and rooting being needed to add certificates to the system store. If you have a rooted Android device and would like to use this guide, add the mitmproxy certificate to the system store instead, and you should be able to follow this guide normally. The reason this works on iOS is that iOS treats system root CAs and user-installed root CAs the same by default, and unless an app uses SSL pinning or some other method to deny user-installed root CAs, it can be HTTPS intercepted via a MiTM attack without a jailbreak needed. If Twilio wants to patch this by implementing SSL pinning, they absolutely can.

## Other info

You can find some more information on the comments of this GitHub Gist: [https://gist.github.com/gboudreau/94bb0c11a6209c82418d01a59d958c93](https://gist.github.com/gboudreau/94bb0c11a6209c82418d01a59d958c93).

If something goes wrong while following this guide, please file a GitHub issue and I will look into it.

---

## Contributing

The guide for contributing is in the [CONTRIBUTING.md](CONTRIBUTING.md) file. If you have any suggestions or improvements, feel free to open an issue or a pull request.

---

## License

### MIT License

This project is licensed under the [MIT License](LICENSE).
