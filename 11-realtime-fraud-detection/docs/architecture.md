# Architecture Details

## Why Kafka?
Kafka siguron durueshmëri (durability) dhe shkallëzim. Nëse procesori dështon, mesazhet mbeten në topic dhe përpunohen kur sistemi të ringrihet.

## Why Redis?
Për llogaritjen e "Velocity" (sa transaksione bëri një përdorues në orën e fundit), kemi nevojë për një counter shumë të shpejtë me TTL (Time To Live). Redis është ideal për këtë.

## ML Model
Përdorim **Isolation Forest**, një algoritëm i pambikëqyrur (unsupervised) ideal për të gjetur anomali në të dhëna financiare ku shembujt e mashtrimit janë të rrallë.