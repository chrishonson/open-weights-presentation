# Hardware context sources

Checked October 25, 2026. These four context slides contain manufacturer specifications and prices, not benchmark results. Existing measured results remain separate.

## Macs

- [Apple US Mac mini store](https://www.apple.com/shop/buy-mac/mac-mini): M6, 16 GB memory, 256 GB storage; $899 base price. Price verified in the store page's embedded currentPrice data.
- [Apple US Mac Studio store](https://www.apple.com/shop/buy-mac/mac-studio): M5 Max, 36 GB / 512 GB, $2,499; M5 Ultra, 96 GB / 1 TB, $5,499. Prices verified in embedded currentPrice data.
- [Apple August 25, 2026 announcement](https://www.apple.com/newsroom/2026/08/apple-introduces-new-mac-studio-with-m5-max-and-m5-ultra/): maximum memory 128 GB (Max), 512 GB (Ultra), requiring paid configuration upgrades.
- [Apple September 2026 desktop release](https://www.apple.com/newsroom/2026/09/the-new-mac-mini-and-mac-studio-are-available-today/): Mac mini / Studio product photo.

Prices are US dollars, before tax; desktops exclude display and peripherals. Advertised memory labels are preserved rather than converted into the decimal units used by the benchmark charts.

## NVIDIA graphics cards

- [NVIDIA January 6, 2025 launch announcement](https://nvidianews.nvidia.com/news/nvidia-blackwell-geforce-rtx-50-series-opens-new-world-of-ai-computer-graphics): RTX 5080 $999, RTX 5090 $1,999 US launch MSRP. These are historical card-only launch prices, not current retail quotes.
- [RTX 5090 specifications and image](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/): 32 GB GDDR7.
- [RTX 5080 specifications](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5080/): 16 GB GDDR7.

## Servers

- [NVIDIA DGX SuperPOD](https://www.nvidia.com/en-us/data-center/dgx-superpod/): illustrative rack image. No claim that this is AWS or DeepInfra infrastructure.
- [NVIDIA L40S](https://www.nvidia.com/en-us/data-center/l40s/): 48 GB GPU memory.
- [AWS G6e](https://aws.amazon.com/ec2/instance-types/g6e/): L40S instance family. Our intended g6e.xlarge configuration is documented in GPU-RUN.md; this addition makes no measured AWS performance claim.

## Offline image credits

Official manufacturer images are stored locally for offline presentation, with original download URLs in [image-sources.json](assets/hardware/image-sources.json). Apple and NVIDIA retain rights to their images. Image credit and source links appear on each slide.

## API economics

[Hugging Face continuous batching documentation](https://huggingface.co/docs/transformers/en/continuous_batching) explains dynamic scheduling at each generation step to improve GPU utilization. The slide's pooled-demand timeline and hardware-cost-per-token relationship are conceptual explanations, not measurements or estimates of DeepInfra's business. Hardware cost is one component; operations, energy, networking and spare capacity remain costs. Higher aggregate throughput is distinct from individual request latency.

## L40S and Blackwell purchase comparison

- [CDW PNY L40S, NVL40STCGPU-KIT](https://www.cdw.com/product/pny-nvidia-quadro-l40s-graphic-card-48-gb-gddr6/7582191): $10,497.99 for one 48 GB GPU card, checked October 25, 2026, and confirmed unchanged by the owner in a browser on October 26, 2026 (CDW blocks automated page loads). Rounded to about $10,500 on slide.
- [Lenovo Press 2026 TCO, HTML edition](https://lenovopress.lenovo.com/lp2368-on-premise-vs-cloud-generative-ai-total-cost-of-ownership-2026-edition): Config C, ThinkSystem SR680a V3 with eight B200 GPUs, usual customer sale price $550,475.10 as of June 15, 2026. Rounded to about $550,000. The linked PDF carries an older January price; the slide uses the updated HTML edition.

Blackwell refers specifically to B200 in this server example. The server price includes the system around eight GPUs; it is not a standalone card quote. Neither public price is evidence of AWS/DeepInfra acquisition cost. Rack imagery illustrates infrastructure rather than the quoted Lenovo configuration.

- [CDW PNY RTX PRO 6000 Blackwell Workstation Edition, VCNRTXPRO6000B-PB](https://www.cdw.com/product/pny-nvidia-rtx-pro-6000-graphic-card-96-gb-gddr7/8326705): one 96 GB GDDR7 card, $19,977.99, checked October 25, 2026. Rounded to about $20,000. This is a different Blackwell GPU from B200; host computer extra.

## Hopper addition

- [NVIDIA H100](https://www.nvidia.com/en-us/data-center/h100/): Hopper architecture, 80 GB for the PCIe variant.
- [Data Power Supply H100 PCIe listing](https://www.datapowersupply.com/copy-of-inventory-3/h100): $30,000–$35,000, volume-based seller range for an 80 GB accelerator, checked October 25, 2026. Host server extra. This is not NVIDIA MSRP or a guaranteed single-unit quote.
- L40S is explicitly labeled Ada Lovelace to distinguish the three architecture families on the slide.


## Architecture and product-class clarification (October 25 review)

NVIDIA’s [RTX 6000 Ada page](https://www.nvidia.com/en-us/products/workstations/rtx-6000/) identifies a 48 GB Ada workstation product. Its [RTX PRO 6000 Blackwell Workstation page](https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000/) identifies 96 GB GDDR7 and Blackwell. The [Hopper architecture page](https://www.nvidia.com/en-us/data-center/technologies/hopper-architecture/) identifies H100/H200 as data-center accelerators. The workstation succession shown is Ada → Blackwell; Hopper is not an RTX workstation generation. Do not confuse a PCIe form factor with a workstation product class. RTX 6000 Ada is now priced: [CDW PNY RTX 6000 Ada, VCNRTX6000ADA-PB](https://www.cdw.com/product/pny-nvidia-rtx-6000-ada-graphic-card-48-gb-gddr6/7275196), $9,605.99, seen in a CDW search result on October 26, 2026 (CDW blocks automated page loads; not yet opened in a browser). Rounded to about $9,600 on the slide. It is the Ada workstation counterpart of the L40S: same 48 GB GDDR6, 18,176 CUDA cores and 568 fourth-generation Tensor cores, but actively cooled with four DisplayPort 1.4a outputs and 300 W ([NVIDIA](https://www.nvidia.com/en-us/products/workstations/rtx-6000/)). The L40S is passively cooled, has no display outputs and draws 350 W. Both are PCIe cards.

## 64 GB Mac comparison — October 26, 2026

Replaces the lower-memory base-price examples on the Macs slide. Both exact product pages publish Product/Offer JSON-LD with USD prices.

- [MacBook Pro, 14-inch, M5 Max Chip, 18-core CPU, 40-core GPU, Space Black, Standard display, 64GB memory, 2TB storage](https://www.apple.com/shop/buy-mac/macbook-pro/14-inch-space-black-standard-display-apple-m5-max-chip-18-core-cpu-40-core-gpu-64gb-memory-2tb-storage): $5,099 before tax, read from Apple's configurator. 64 GB requires the 40-core GPU, and the M5 Max laptop starts at 2 TB, so this is the cheapest 64 GB M5 Max MacBook Pro. It replaces the 14-inch M5 Pro (64 GB / 1 TB, $3,699). Image credit: Apple; local file `assets/hardware/macbook64.jpg`.
- [Mac Studio, M5 Max Chip, 18-core CPU, 40-core GPU, 64GB memory, 1TB storage](https://www.apple.com/shop/buy-mac/mac-studio/m5-max-chip-18-core-cpu-40-core-gpu-64gb-memory-1tb-storage): $3,799 before tax. Image credit: Apple; local file `assets/hardware/studio64.jpg`.

Owner reports paying $2,500 for the tested 64 GB M1 Max MacBook Pro in January 2024. That is a historical personal purchase, not a current market quote. New machines were not benchmarked.

## Chip and card specifications (checked Oct 26, 2026)

- [M1 Max MacBook Pro 14-inch specs](https://support.apple.com/en-us/111901): 10-core CPU (8 performance, 2 efficiency), 32-core GPU, 16-core Neural Engine, 400 GB/s. The tested Mac's core counts match `system_profiler`.
- [MacBook Pro specs](https://www.apple.com/macbook-pro/specs/): M5 Max 18-core CPU (6 super, 12 performance), 40-core GPU, 16-core Neural Engine, 614 GB/s.
- [Mac Studio specs](https://www.apple.com/mac-studio/specs/): M5 Max 18-core CPU (6 super, 12 performance), 40-core GPU, 16-core Neural Engine, 614 GB/s for the 40-core GPU configuration.
- [RTX 5090 specs](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/): 21,760 CUDA cores, 32 GB GDDR7, 512-bit, 575 W. The 1,792 GB/s bandwidth and 680 Tensor cores are not on that page.
- [L40S specs](https://www.nvidia.com/en-us/data-center/l40s/): Ada Lovelace, 48 GB GDDR6 with ECC, 864 GB/s, 18,176 CUDA cores, 568 fourth-generation Tensor cores, 350 W. Price on the GPUs slide is the CDW listing above, rounded to about $10,500.
- [RTX PRO 5000 Blackwell specs](https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-5000/): 48 GB or 72 GB GDDR7 with ECC, 1,344 GB/s, 5th-gen Tensor cores, 300 W. NVIDIA's page gives no core counts. 14,080 CUDA and 440 Tensor cores come from reseller listings.
- RTX PRO 5000 72 GB price: $11,999 MSRP on the [SHI listing](https://www.shi.com/product/50915088/NVIDIA-RTX-PRO-5000-BLACKWELL-72GB-GCARD-SCB-RETAIL), seen through web search. SHI and CDW block automated page loads, so the listing was not opened directly.
- The GPUs slide shows the RTX PRO 5000 72 GB (closest in memory to the 64 GB Macs) and the L40S (the card tested on AWS). They replace the 16 GB RTX 5080 and 32 GB RTX 5090. Image: NVIDIA RTX PRO 5000 product page, local file `assets/hardware/rtx-pro-5000.jpg`.
- Servers slide photo: [NVIDIA DGX SuperPOD photo](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/dgx-superpod-gb200/nvidia-dgx-superpod-1920x1020.jpg), 1920x1080, used on the [DGX B200 page](https://www.nvidia.com/en-us/data-center/dgx-b200/). Stored as `assets/hardware/superpod.jpg`. The slide shows a wide strip of it, centred on the NVIDIA logo row. It replaces a 1200x630 SuperPOD render that blurred when enlarged.


## GPU comparison refresh — October 26, 2026

The RTX PRO 5000 Blackwell 72 GB is close in memory capacity to the 64 GB Macs, but its dedicated GPU memory is different from system-shared memory. NVIDIA confirms the 72 GB variant: https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-5000/ . SHI lists $12,194 (backordered), with $11,999 in its MSRP field: https://www.shi.com/product/50915088/NVIDIA-RTX-PRO-5000-BLACKWELL-72GB-GCARD-SCB-RETAIL . These are card-only prices; this card was not benchmarked.
