# 📚 OpinionLens — Comprehensive Dataset & Tooling Catalog

This catalog documents all baseline, integrated, and verified external datasets and discovery tools for OpinionLens, along with compatibility ratings, schema mapping instructions, and multilingual guidance.

---

## 1. Pre-Packaged & Indexed Datasets in Repository

These datasets are included directly in the `dataset/` directory, pre-trained, and indexed into ChromaDB collections:

| Dataset | Category | Source & Benchmark | Flagship Models & Aspect Benchmarks |
|---|---|---|---|
| **`dataset/cpsc_safety_incidents.csv`** | Consumer Safety & Hardware Recalls | [CPSC SaferProducts.gov](https://www.saferproducts.gov/) (10,089 real incident reports) | • Ground truth evaluation dataset for OpinionLens **Critical-Minority Safety Guard**.<br>• Covers real fire hazards, battery explosions, burns, electrical shocks, child safety risks. |
| **`dataset/mams_aspects.csv`** | Multi-Aspect Multi-Sentiment Suite | [MAMS ABSA Benchmark](https://github.com/siat-nlp/MAMS-for-ABSA) (4,297 sentences) | • Benchmark dataset where every sentence contains multiple conflicting aspects.<br>• Evaluates OpinionLens's **Contested Viewpoint Detection** algorithm (`CONTESTED_MIN_RATIO = 0.20`). |
| **`dataset/semeval_laptops.csv`** | Laptop Hardware ABSA Benchmark | [SemEval-2014 Task 4](https://huggingface.co/datasets/tomaarsen/setfit-absa-semeval-laptops) (1,479 reviews) | • Human-annotated laptop aspect targets (`screen`, `battery`, `keyboard`, `OS`, `performance`) with ground-truth polarities. |
| **`dataset/fake_reviews_benchmark.csv`** | Deceptive & AI Opinion Spam | [Fake Reviews Benchmark](https://huggingface.co/datasets/debojit01/fake-review-dataset) (1,000 reviews) | • Real vs. computer-generated (CG) fake reviews across home, kitchen, and electronics.<br>• Validates OpinionLens detection of counterfeit goods and promotional spam. |
| **`dataset/tablets_ereaders.csv`** | Tablets & E-Readers | Modern Tech Hardware Corpus | • **Apple iPad Pro 12.9 M2** (`IPAD_PRO_M2`): Liquid Retina XDR display, Apple Pencil hover, iPadOS multitasking, USB-C port sparking.<br>• **Amazon Kindle Paperwhite 11** (`KINDLE_PAPERWHITE_11`): 300 ppi glare-free warm light, 10-week battery, UI responsiveness, wireless charging pad heat. |
| **`dataset/pc_gaming_laptops.csv`** | PC Gaming Laptops & Creators | High-TDP Hardware Corpus | • **ASUS ROG Zephyrus G14** (`ASUS_ROG_G14`): 3K 120Hz OLED, Ryzen 9 / RTX 4070, fan coil whine, keyboard deck heat, 240W power brick scorch.<br>• **HP Omen 16** (`HP_OMEN_16`): Intel i7-14700HX / RTX 4060, 240Hz QHD display, screen wobble, battery swelling trackpad displacement. |
| **`dataset/bose_audio.csv`** | Premium ANC Headphones | Acoustic Hardware ABSA Corpus | • **Bose QuietComfort 45** (`BOSE_QC45`): Class-leading flight ANC, plush ear cushions, wind noise buffeting, earcup lithium battery overheating hazard. |
| **`dataset/smart_appliances.csv`** | Smart Kitchen Appliances | Connected Home Hardware Corpus | • **Instant Pot Duo Plus** (`INSTANT_POT_DUO`): 9-in-1 multi-cooker, stainless pot, food burn sensor halts, steam release valve spray burns.<br>• **Ninja Air Fryer Max XL** (`NINJA_AIR_FRYER`): 450F Max Crisp, basket ceramic coating peel, plastic burning smell, heavy power cord melting outlet. |
| **`dataset/laptops.csv`** | High-Performance Laptops | [SemEval-2016 Task 5](https://alt.qcri.org/semeval2016/task5/) & Tech Reviews | • **Apple MacBook Air M2** (`MACBOOK_AIR_M2`): Fanless thermal throttling, Liquid Retina display, MagSafe charger sparks, keyboard feel.<br>• **Dell XPS 15 9530** (`DELL_XPS_15`): 3.5K OLED touchscreen, RTX 4060 creative workflows, fan noise, 130W charger brick heat, trackpad lift.<br>• **Lenovo ThinkPad X1 Carbon Gen 11** (`THINKPAD_X1_CARBON`): Legendary tactile keyboard, matte anti-glare screen, TrackPoint, Thunderbolt port electrical spark risk. |
| **`dataset/audio_headphones.csv`** | Wireless Audio & ANC Headphones | Acoustic Hardware ABSA Corpus | • **Sony WH-1000XM4** (`SONY_WH1000XM4`): Active Noise Cancellation (ANC), LDAC high-res audio, 30-hour battery, muffled Zoom call mic, ear cup battery overheating.<br>• **Apple AirPods Pro 2** (`AIRPODS_PRO_2`): Adaptive Transparency, spatial audio, ear tip pressure headache, MagSafe case overheating/smoking, silicone ear rash. |
| **`dataset/smartwatches.csv`** | Smartwatches & Health Wearables | Wearable Sensor & Health Benchmarks | • **Apple Watch Series 8** (`APPLE_WATCH_S8`): Always-On Retina display, ECG/Crash detection, 18-hr daily battery debate, optical sensor skin burn/blister, swollen battery screen popping.<br>• **Samsung Galaxy Watch 5** (`GALAXY_WATCH_5`): Sapphire crystal scratch resistance, BIA body composition, non-Samsung phone ECG restrictions, wireless charging puck overheating. |
| **`dataset/gaming_consoles.csv`** | Next-Gen Consoles & Handhelds | Console Hardware & Gaming ABSA | • **Sony PlayStation 5 Disc Edition** (`PS5_CONSOLE`): 4K 60/120Hz ray tracing, Gen4 SSD zero-load times, DualSense haptic triggers, analog stick drift, power supply sparks/smoke, vertical liquid metal pooling.<br>• **Valve Steam Deck OLED** (`STEAM_DECK_OLED`): 90Hz OLED HDR display, SteamOS suspend/resume, AAA game 2-hr battery drain, chunky handheld weight, USB-C port melting. |
| **`dataset/smart_home.csv`** | Smart Home & Security IoT | IoT Assistant & Smart Device Corpus | • **Amazon Echo Dot Gen 5** (`ECHO_DOT_GEN5`): Upgraded bass sphere, far-field Alexa voice pickup, temperature automation, unsolicited promo suggestions, 15W power adapter melting outlet.<br>• **Google Nest Cam Battery** (`NEST_CAM_INDOOR`): 1080p HDR night vision, on-device AI person/car detection, magnetic quick-mount, winter battery drain, continuous streaming overheating. |
| **`dataset/amazon_electronics.csv`** | Power Banks & Chargers | [McAuley-Lab Amazon 2023](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023) | **Anker PowerCore 20100mAh** (`B00X5RV14Y`): High-capacity multi-device charging, heavy pocket bulk, lithium battery swelling, smoke hazard during recharge. |
| **`dataset/lenova.csv`** (and 9 others) | Mobile Smartphones (Flipkart Baseline) | [Mendeley Data `wzxkx2kr6n.1`](https://data.mendeley.com/datasets/wzxkx2kr6n/1) | 10 major brands (`samsung.csv`, `iphone.csv`, `lenova.csv`, `moto.csv`, `nokia.csv`, `redmi.csv`, `micromax.csv`, `panasonic.csv`, `oppo.csv`, `vivo.csv`). Over 200,000 real e-commerce reviews with reviewer IDs and helpful votes. |

---

## 2. Evaluation of User-Submitted Datasets

All links shared by the user were evaluated for schema compatibility, semantic quality, and aspect-level suitability.

### 🌟 Tier A: Gold Standard for Aspect-Level Extraction & Evaluation
1. **[SemEval-2016 Task 5 (ABSA Benchmark)](https://alt.qcri.org/semeval2016/task5/)**
   - **Suitability:** ⭐⭐⭐⭐⭐ (Industry Standard Benchmark)
   - **Verdict:** Directly adopted into our laptop test suite and `dataset/laptops.csv`. SemEval provides human-annotated aspect target terms and polarity labels (Positive, Negative, Neutral, Conflict), serving as the ground truth for evaluating OpinionLens extraction accuracy.
2. **[McAuley-Lab/Amazon-Reviews-2023 (Hugging Face)](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023)**
   - **Suitability:** ⭐⭐⭐⭐⭐ (Massive Modern Corpus)
   - **Verdict:** High-volume corpus with verified purchase tags, timestamps, and helpfulness metrics. Ideal for scaling cross-domain products (headphones, smart home, appliances). Compatible via our JSON/CSV loader.
3. **[IEEE Dataport: Mobile Review Dataset for Aspect-Level Sentiment Analysis](https://ieee-dataport.org/documents/mobile-review-dataset-aspect-level-sentiment-analysis)**
   - **Suitability:** ⭐⭐⭐⭐⭐ (Peer-Reviewed Mobile ABSA)
   - **Verdict:** Highly curated aspect tags (screen, battery, camera, software) on smartphone customer reviews. Compatible directly with `dataset_loader.py`.
4. **[Mendeley Tech Product Reviews Dataset (8cszh3bwbb/1)](https://data.mendeley.com/datasets/8cszh3bwbb/1)**
   - **Suitability:** ⭐⭐⭐⭐⭐ (Structured Tech Reviews)
   - **Verdict:** Clean English reviews across electronics with hardware-specific sentiment tags.

### 🛒 Tier B: E-Commerce & Smartphone Customer Sentiment (Kaggle)
1. **[Flipkart Product Review Dataset (mansithummar67)](https://www.kaggle.com/datasets/mansithummar67/flipkart-product-review-dataset)**
   - **Suitability:** ⭐⭐⭐⭐ (Real-world Indian E-commerce)
   - **Verdict:** Contains buyer reviews, verified purchase flags, and ratings. Compatible with drag-and-drop uploader.
2. **[Global Mobile Reviews Dataset 2025 Edition (mohankrishnathalla)](https://www.kaggle.com/datasets/mohankrishnathalla/mobile-reviews-sentiment-and-specification)**
   - **Suitability:** ⭐⭐⭐⭐⭐ (Modern 2025 Specs & Reviews)
   - **Verdict:** Pairs phone specifications (chipset, battery mAh, camera MP) with sentiment. Highly recommended for correlating specs with customer complaints.
3. **[Amazon Reviews: Unlocked Mobile Phones (grikomsn)](https://www.kaggle.com/datasets/grikomsn/amazon-cell-phones-reviews)**
   - **Suitability:** ⭐⭐⭐⭐ (Broad Coverage)
   - **Verdict:** Over 400 models; clean columns (`Brand`, `Model`, `Price`, `Rating`, `Reviews`, `Votes`).
4. **[Electronic Products Customer Review (samuelkamau)](https://www.kaggle.com/datasets/samuelkamau/electronic-products-customer-review)**
   - **Suitability:** ⭐⭐⭐⭐ (Consumer Electronics)
   - **Verdict:** Covers diverse consumer hardware (speakers, headphones, chargers, cameras).
5. **[Apple of the Customer's Eyes: iPhone Reviews (tbtfanalystspro)](https://www.kaggle.com/datasets/tbtfanalystspro/iphone-reviews)**
   - **Suitability:** ⭐⭐⭐⭐ (Brand-Specific Deep Dive)
   - **Verdict:** Focuses on iPhone generation comparisons (battery degradation, iOS updates, camera quality).
6. **[GD Dataset (soul81)](https://www.kaggle.com/datasets/soul81/gd-dataset/)**
   - **Suitability:** ⭐⭐⭐ (General Domain Sentiment)
   - **Verdict:** Good for general sentiment testing.

### 🌐 Tier C: Multilingual E-Commerce Datasets (Mendeley)
1. **[Kannada_dataset_Amazon_Website (krxvrbwctn/1)](https://data.mendeley.com/datasets/krxvrbwctn/1)**
2. **[BanglaEcomReviewCorpus (kkzfrvhbhp/1)](https://data.mendeley.com/datasets/kkzfrvhbhp/1)**
3. **[Daraz BD Products & Reviews (k5b6vxv25r/1)](https://data.mendeley.com/datasets/k5b6vxv25r/1)**
4. **[RevBangla (bnbbcdsf4m/1)](https://data.mendeley.com/datasets/bnbbcdsf4m/1)**
5. **[ShoppingAppReviews Dataset (chr5b94c6y/1)](https://data.mendeley.com/datasets/chr5b94c6y/1)**
6. **[Mendeley 797tygyzbn/2 & n3wm4xbs5n/2](https://data.mendeley.com/datasets/797tygyzbn/2)**

> [!IMPORTANT]
> **Multilingual Embedding Note:**
> OpinionLens's default embedding model is `BAAI/bge-small-en-v1.5` (an English-specific embedding model).
> To index and retrieve Kannada or Bengali reviews natively without translation:
> 1. In `config.py`, change `EMBEDDING_MODEL` to a multilingual transformer such as:
>    ```python
>    EMBEDDING_MODEL = "BAAI/bge-m3"  # 100+ languages, SOTA retrieval
>    # or
>    EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
>    ```
> 2. Re-index the dataset using `ingest.py` or the sidebar UI.

---

## 3. Dataset Discovery Tools Evaluated

| Tool | Link | Purpose & How to Use with OpinionLens |
|---|---|---|
| **Google Dataset Search** | [datasetsearch.research.google.com](https://datasetsearch.research.google.com/) | Premier search engine for academic & open-license review corpora. Search query: `"aspect based sentiment analysis" filetype:csv`. |
| **Daseen** | [daseen.de](https://www.daseen.de) | Meta-search engine index for tabular datasets and German/European open repositories. |
| **Dateno.io** | [dateno.io](https://dateno.io/) | High-speed data discovery platform indexing public data dumps and Parquet tables. |
| **Hugging Face Similar** | [Chrome Extension](https://chromewebstore.google.com/detail/hugging-face-similar/aijelnjllajooinkcpkpbhckbghghpnl) | Browser extension that embeds the Hugging Face dataset catalog to find structurally similar datasets when browsing Kaggle or GitHub. |

---

## 4. How to Ingest Any Dataset in 30 Seconds

OpinionLens includes a **Universal Schema Loader** (`dataset_loader.py`) with fuzzy column matching and automatic encoding detection (`utf-8`, `latin1`, `utf-8-sig`).

### Method A: Web UI Drag & Drop (Zero Code)
1. Run `run.bat` or `streamlit run app.py`.
2. Expand the sidebar: **"Custom Dataset Connector"**.
3. Upload any CSV or JSON file from Kaggle, Mendeley, or Hugging Face.
4. Click **"Activate Dataset Now"** — it instantly becomes selectable in the main Brand dropdown!

### Method B: Command-Line Ingestion (Batch Processing)
Save your CSV file into `dataset/my_dataset.csv`, then run:
```bash
python ingest.py --csv my_dataset.csv --product_id MY_PRODUCT_01 --max_reviews 200
```
OpinionLens will compute embeddings on CPU/GPU and cache the vector collection in `chroma_db/` for millisecond-speed retrieval.

---

## 5. Mega-Scale Corpora for Universal Product Coverage (100M+ Reviews)

To ensure a user is **never disappointed by missing their specific product or gadget** (MacBooks, ThinkPads, ROG gaming laptops, iPhones, Galaxy flagships, Pixel devices, AirPods, Sony ANC headphones, Bose, Steam Deck, PS5, Xbox, smart home IoT, wearables, and appliances), the following massive open corpora provide 100% relatable real-world coverage:

### 🚀 Mega Corpus 1: McAuley-Lab Amazon Reviews 2023 (571 Million Reviews)
- **Source:** [Hugging Face `McAuley-Lab/Amazon-Reviews-2023`](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023)
- **Scale:** 571.43 Million customer reviews across 33 product categories; tens of millions of distinct products (ASINs).
- **Relatable Subsets for OpinionLens:**
  - `raw_review_Computers` (20M+ reviews): Laptops, GPUs, SSDs, monitors, RAM, keyboards.
  - `raw_review_Electronics` (43M+ reviews): Audio, headphones, cameras, TV, charging gear.
  - `raw_review_Cell_Phones_and_Accessories` (35M+ reviews): All smartphone generations & accessories.
  - `raw_review_Video_Games` (13M+ reviews): Consoles (PS5, Xbox, Switch), handhelds (Steam Deck), controllers.
  - `raw_review_Appliances` (2.5M+ reviews): Air fryers, robot vacuums, microwaves, kitchen IoT.
- **Direct Schema Mapping:**
  - `text` -> `review_text`
  - `rating` -> `rating`
  - `parent_asin` / `asin` -> `product_id`
  - `title` -> `review_title`
  - `user_id` -> `reviewer_id`
  - `helpful_vote` -> `helpful_votes`
  - `timestamp` -> `date`

### 📦 Mega Corpus 2: Amazon Customer Reviews on AWS Open Data (130+ Million Reviews)
- **Source:** [AWS Open Data Registry `amazon-reviews-pds`](https://registry.opendata.aws/amazon-reviews/)
- **Access:** Direct public S3 / HTTPS GZipped TSV files (no API key required).
- **Key Files:**
  - `https://s3.amazonaws.com/amazon-reviews-pds/tsv/amazon_reviews_us_PC_v1_00.tsv.gz` (6.9M reviews)
  - `https://s3.amazonaws.com/amazon-reviews-pds/tsv/amazon_reviews_us_Wireless_v1_00.tsv.gz` (9.0M reviews)
  - `https://s3.amazonaws.com/amazon-reviews-pds/tsv/amazon_reviews_us_Electronics_v1_00.tsv.gz` (3.1M reviews)
  - `https://s3.amazonaws.com/amazon-reviews-pds/tsv/amazon_reviews_us_Video_Games_v1_00.tsv.gz` (1.8M reviews)
  - `https://s3.amazonaws.com/amazon-reviews-pds/tsv/amazon_reviews_us_Watches_v1_00.tsv.gz` (960K reviews)
  - `https://s3.amazonaws.com/amazon-reviews-pds/tsv/amazon_reviews_us_Major_Appliances_v1_00.tsv.gz` (96K reviews)

### 🚨 Mega Corpus 3: CPSC Public Product Safety Incidents & Recalls
- **Source:** [SaferProducts.gov](https://www.saferproducts.gov/) / CPSC Public Data Export
- **Scale:** 50,000+ consumer incident reports detailing safety hazards (battery fire, burn, overheating, electric shock).
- **Purpose:** Primary evaluation dataset for OpinionLens's Critical-Minority Safety Guard.

### 🎮 Mega Corpus 4: Steam Game & Handheld Hardware Reviews
- **Source:** [Hugging Face `steam_reviews`](https://huggingface.co/datasets/steam_reviews) / Kaggle
- **Scale:** 21+ Million reviews.
- **Relatability:** Real-world performance feedback on hardware handhelds (Steam Deck, ROG Ally) and games. Contains framerate drops, crashes, thermal stuttering, and controller mapping feedback.
