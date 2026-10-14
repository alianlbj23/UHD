# DIY W-HUD 抬頭顯示器：簡易測試版（Jetson 開發，可移植樹莓派）

依照《W-HUD 簡易測試版材料清單》實作：螢幕平放在儀表板上，畫面反射到擋風玻璃。
畫面是黑底，顯示白色大箭頭、距離數字、路名和一行假歌詞，整個畫面左右鏡像。

程式只用 Python + pygame，**不依賴 Jetson 專用的函式庫**，所以之後移植到 Raspberry Pi 5 不用改程式碼。

```
車用電源 ──► Jetson ──(HDMI / DP→HDMI)──► 7 吋 HDMI 螢幕（平放、畫面朝上）──反射──► 擋風玻璃
                 └──USB-A──► 螢幕供電
```

## 1. 硬體：用 Jetson 取代 Pi 5 時要改的地方

PDF 的材料清單是照 Pi 5 寫的。換成 Jetson 時，**影像線**和**車上供電**這兩項要改：

| 項目 | Jetson Orin Nano 開發套件（含 Super） | Jetson Nano 4GB (B01) | Jetson Xavier NX 開發套件 |
|---|---|---|---|
| 影像輸出 | **只有 DisplayPort** → 買 DP 轉 HDMI 線（被動式即可） | HDMI，一般 HDMI 線 | HDMI，一般 HDMI 線 |
| 主機供電 | DC 圓孔 19V（原廠變壓器） | DC 圓孔 5V 4A（需短接 J48）或 micro-USB 5V 2A | DC 圓孔 19V |
| 螢幕供電 | 螢幕 USB 接 Jetson 的 USB-A | 同左 | 同左 |

**車上供電（測試階段）**

- PDF 寫的「車用 USB-C 5V 3A 快充」**沒辦法帶 Orin Nano 或 Xavier NX**，因為它們要 19V。
- 最簡單、最安全的做法：用點菸座**電源逆變器**（12V 轉 110V，150W 以上），插原廠變壓器。
- 也可以用 PD 快充（65W 以上）加「USB-C PD 誘騙線，20V 轉 DC 5.5×2.5mm」。買之前先確認你的載板接受 20V 輸入。
- Jetson Nano 4GB 可以接 5V，但車充加上螢幕常常會電壓不足而降頻。測試時可接受，正式版要改用 DC 圓孔供電。
- 熄火或發動時電源會瞬斷，可能損壞 SD 卡。測試時最好先停車並維持供電，結束後在終端機下 `sudo shutdown now`。

其餘材料照 PDF 準備即可：Waveshare 7 吋 HDMI LCD、反射膜（選購）、防滑墊（選購）。
另外建議準備一個**小型無線鍵盤或數字鍵盤**，在車上調整畫面時會用到。

## 2. 安裝（在 Jetson 上）

```bash
git clone <本專案> ~/whud    # 或直接把資料夾複製過去
cd ~/whud
./scripts/install.sh --autostart   # 安裝 pygame、中文字型，並設定開機自動啟動
./scripts/run.sh                   # 全螢幕執行
```

想讓 Jetson 開機後直接顯示 HUD，還要打開自動登入（腳本最後會提示怎麼做）：
在 `/etc/gdm3/custom.conf` 的 `[daemon]` 底下加入 `AutomaticLoginEnable=true` 和 `AutomaticLogin=<你的帳號>`。

**在電腦上預覽**（不必接螢幕，任何 Linux、Mac 或 Windows 都可以）：

```bash
python -m whud --windowed --no-mirror               # 視窗模式、不鏡像，直接看
python -m whud --snapshot out.png --calibration     # 不開視窗，輸出一張校正畫面
```

## 3. 按鍵操作

方向一律以**你在擋風玻璃反射中看到的畫面**為準。例如按「→」，反射畫面就往右移。

| 按鍵 | 功能 | 按鍵 | 功能 |
|---|---|---|---|
| `H` | 開關左右鏡像 | `G` | 切換到校正格線 |
| `V` | 開關上下翻轉 | `空白鍵` | 暫停或繼續 demo |
| 方向鍵（加 Shift 移得更快） | 移動畫面 | `N` | 跳到下一個路口 |
| `+` / `-` | 縮放 | `C` | 換顏色（白、綠、琥珀、青） |
| `[` / `]` | 軟體亮度 | `S` | **儲存設定**（存到 config.json，下次開機沿用） |
| `P` | 截圖 | `R` | 重設 |
| `Esc` / `Q` | 離開 | | |

每次按鍵後，畫面上方會顯示目前的設定 3 秒。這行提示也有鏡像，在反射中看得懂。

## 4. 測試步驟（對應 PDF 第四、五節）

1. **室內確認**：執行 `./scripts/run.sh`，按 `G` 開校正畫面。直接看螢幕時，F 和文字是反的，這是正常的。拿鏡子照螢幕，鏡子裡的 F 是正的就代表方向正確。
2. **上車擺放**：停好車，螢幕平放在駕駛座前方的儀表板上，畫面朝上。
3. **方向**：反射中的文字如果上下顛倒，按 `V`；左右相反，按 `H`。
4. **位置與大小**：用方向鍵和 `+`/`-` 把畫面移到視線前方，但不要擋到路面。
5. **變形**：在校正畫面上，如果圓看起來是橢圓，或格線變成梯形，就把螢幕前後移動、調整角度。
6. **雙影**：比較貼反射膜和不貼的差異。
7. **亮度**：在傍晚或晚上測試。太刺眼就按 `[` 壓暗，或按 `C` 改用綠色、琥珀色。
8. 按 `S` 存檔，再按 `P` 截圖，同時用手機拍下反射效果，當作正式版的依據。

> 軟體亮度只會把像素調暗，**沒辦法調 HDMI 螢幕的背光**，所以黑底還是會微微發光。白天看不清楚是正常的，正式版會換高亮度螢幕。

## 5. 程式架構

```
whud/
  sources.py   HudState（箭頭、距離、路名、歌詞）與 DemoSource（假路線倒數）
  render.py    繪製 HUD 與校正畫面；compose() 處理縮放、位移、亮度、鏡像
  app.py       主迴圈與按鍵
  config.py    設定預設值與 config.json 讀寫
  fonts.py     自動尋找中文字型（Noto Sans CJK）
scripts/       install.sh、run.sh
tests/         pytest
```

升級成正式版時，只要另寫一個資料來源（例如 GPS 或 iPhone ANCS/AMS），回傳同樣的 `HudState`，
再到 `app.py` 把 `DemoSource` 換掉即可，繪圖和鏡像的部分都不用動。

執行測試：`pip install -r requirements-dev.txt && python -m pytest -q`

## 6. 之後移植到 Raspberry Pi 5

程式碼不用改。

1. 用 Raspberry Pi OS (Bookworm, 64-bit) 燒錄 SD 卡，把專案複製過去，執行 `./scripts/install.sh --autostart`。
2. 執行 `sudo raspi-config`：
   - System Options → Auto Login → Desktop Autologin
   - Display Options → Screen Blanking → 關閉
3. 硬體回到 PDF 的配置：micro-HDMI 轉 HDMI 線，加上車用 USB-C PD 5V 3A 快充。

Pi 5 的效能跑這個程式綽綽有餘。在 Jetson 上調好的 `config.json` 也可以直接複製過去使用。
# UHD
# UHD
# UHD
# UHD
