#!/usr/bin/env python3
"""
Script Load Test hiệu năng cho Wine Quality Prediction API
Hỗ trợ:
- Warm-up hệ thống trước khi đo
- Concurrency N users gửi liên tục trong T giây
- Mỗi request sinh một X-Request-ID duy nhất (UUID4)
- Thu thập và tính toán: total requests, success, errors, error_rate, throughput (req/s),
  p50, p90, p95, p99 latency (ms).
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from typing import Any, Dict, List
import uuid

import httpx
import numpy as np

# Thiết lập UTF-8 cho Windows console nếu cần
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Cấu hình logging (tắt log chi tiết của httpx/httpcore khi load test)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger("load_test")

# Payload mẫu 11 thuộc tính hóa lý rượu vang đỏ
SAMPLE_PAYLOAD = {
    "fixed acidity": 7.4,
    "volatile acidity": 0.7,
    "citric acid": 0.0,
    "residual sugar": 1.9,
    "chlorides": 0.076,
    "free sulfur dioxide": 11.0,
    "total sulfur dioxide": 34.0,
    "density": 0.9978,
    "pH": 3.51,
    "sulphates": 0.56,
    "alcohol": 9.4
}


async def run_warmup(url: str, num_requests: int = 20) -> None:
    """Gửi các request warm-up trước khi đo chính thức (không tính vào metric benchmark)."""
    logger.info("=== BẮT ĐẦU WARM-UP (%d requests) ===", num_requests)
    async with httpx.AsyncClient(timeout=10.0) as client:
        success = 0
        for i in range(num_requests):
            req_id = f"warmup-{uuid.uuid4().hex[:8]}"
            headers = {
                "Content-Type": "application/json",
                "X-Request-ID": req_id
            }
            try:
                resp = await client.post(url, json=SAMPLE_PAYLOAD, headers=headers)
                if resp.status_code == 200:
                    success += 1
            except Exception as e:
                logger.warning("Warm-up request %d failed: %s", i + 1, e)
    logger.info("=== HOÀN TẤT WARM-UP: %d/%d requests thành công (KHÔNG tính vào benchmark) ===\n", success, num_requests)


async def worker(
    worker_id: int,
    url: str,
    stop_event: asyncio.Event,
    latencies: List[float],
    status_counts: Dict[int, int],
    sample_request_ids: List[str]
) -> None:
    """Worker mô phỏng 1 user gửi request liên tục cho đến khi stop_event được kích hoạt."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        while not stop_event.is_set():
            req_id = f"load-{worker_id}-{uuid.uuid4().hex[:12]}"
            if len(sample_request_ids) < 10:
                sample_request_ids.append(req_id)

            headers = {
                "Content-Type": "application/json",
                "X-Request-ID": req_id
            }
            t0 = time.perf_counter()
            try:
                resp = await client.post(url, json=SAMPLE_PAYLOAD, headers=headers)
                t1 = time.perf_counter()
                latency_ms = (t1 - t0) * 1000.0

                code = resp.status_code
                status_counts[code] = status_counts.get(code, 0) + 1

                if code == 200:
                    latencies.append(latency_ms)
                else:
                    status_counts["error"] = status_counts.get("error", 0) + 1
            except Exception as exc:
                t1 = time.perf_counter()
                status_counts["error"] = status_counts.get("error", 0) + 1
                status_counts["exception"] = status_counts.get("exception", 0) + 1


async def execute_load_test(
    url: str,
    concurrency: int,
    duration: float,
    warmup: int = 20
) -> Dict[str, Any]:
    """Thực thi một kịch bản load test với concurrency và duration xác định."""
    # 1. Warm-up
    if warmup > 0:
        await run_warmup(url, warmup)

    # 2. Chuẩn bị biến thu thập dữ liệu
    latencies: List[float] = []
    status_counts: Dict[Any, int] = {}
    sample_request_ids: List[str] = []
    stop_event = asyncio.Event()

    logger.info("=== BẮT ĐẦU LOAD TEST: Concurrency=%d, Duration=%.1fs, Endpoint=%s ===", concurrency, duration, url)
    start_time = time.perf_counter()

    # 3. Tạo các worker concurrent
    tasks = [
        asyncio.create_task(
            worker(i, url, stop_event, latencies, status_counts, sample_request_ids)
        )
        for i in range(concurrency)
    ]

    # 4. Chờ đúng thời lượng duration
    await asyncio.sleep(duration)
    stop_event.set()

    # 5. Chờ toàn bộ worker kết thúc
    await asyncio.gather(*tasks)
    total_elapsed = time.perf_counter() - start_time

    # 6. Tính toán các chỉ số
    successful_requests = len(latencies)
    failed_requests = status_counts.get("error", 0)
    total_requests = successful_requests + failed_requests
    error_rate = (failed_requests / total_requests * 100.0) if total_requests > 0 else 0.0
    throughput = total_requests / total_elapsed if total_elapsed > 0 else 0.0

    if latencies:
        arr = np.array(latencies)
        p50 = float(np.percentile(arr, 50))
        p90 = float(np.percentile(arr, 90))
        p95 = float(np.percentile(arr, 95))
        p99 = float(np.percentile(arr, 99))
        min_lat = float(np.min(arr))
        max_lat = float(np.max(arr))
        mean_lat = float(np.mean(arr))
    else:
        p50 = p90 = p95 = p99 = min_lat = max_lat = mean_lat = 0.0

    results = {
        "endpoint": url,
        "concurrency": concurrency,
        "duration_configured_s": duration,
        "duration_actual_s": round(total_elapsed, 2),
        "warmup_requests": warmup,
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "error_rate_pct": round(error_rate, 3),
        "throughput_req_per_s": round(throughput, 2),
        "latency_p50_ms": round(p50, 2),
        "latency_p90_ms": round(p90, 2),
        "latency_p95_ms": round(p95, 2),
        "latency_p99_ms": round(p99, 2),
        "latency_min_ms": round(min_lat, 2),
        "latency_max_ms": round(max_lat, 2),
        "latency_mean_ms": round(mean_lat, 2),
        "sample_request_ids": sample_request_ids[:5],
        "status_distribution": {str(k): v for k, v in status_counts.items()}
    }

    # In kết quả dạng bảng
    print("\n" + "=" * 60)
    print(f"KET QUA LOAD TEST (Concurrency: {concurrency}, Duration: {round(total_elapsed, 1)}s)")
    print("=" * 60)
    print(f"Endpoint             : {url}")
    print(f"Concurrency          : {concurrency} users")
    print(f"Duration thuc te     : {round(total_elapsed, 2)} s")
    print(f"Total Requests       : {total_requests}")
    print(f"Successful Requests  : {successful_requests}")
    print(f"Failed Requests      : {failed_requests}")
    print(f"Error Rate           : {round(error_rate, 3)} % (Target: < 1%)")
    print(f"Throughput           : {round(throughput, 2)} requests/s")
    print(f"p50 Latency          : {round(p50, 2)} ms ({round(p50 / 1000, 3)} s)")
    print(f"p90 Latency          : {round(p90, 2)} ms ({round(p90 / 1000, 3)} s)")
    print(f"p95 Latency          : {round(p95, 2)} ms ({round(p95 / 1000, 3)} s) (Target: < 2000 ms)")
    print(f"p99 Latency          : {round(p99, 2)} ms ({round(p99 / 1000, 3)} s)")
    print(f"Min / Mean / Max     : {round(min_lat, 2)} / {round(mean_lat, 2)} / {round(max_lat, 2)} ms")
    print(f"Sample Request IDs   : {', '.join(sample_request_ids[:3])}")
    print("=" * 60 + "\n")

    return results


def main():
    parser = argparse.ArgumentParser(description="Wine Quality Load Test Script")
    parser.add_argument("--url", default="http://127.0.0.1:5000/api/predict", help="Endpoint API to test")
    parser.add_argument("--concurrency", type=int, default=10, help="Number of concurrent users")
    parser.add_argument("--duration", type=float, default=60.0, help="Duration in seconds")
    parser.add_argument("--warmup", type=int, default=20, help="Number of warmup requests")
    parser.add_argument("--output", default=None, help="Path to save JSON results")
    args = parser.parse_args()

    results = asyncio.run(execute_load_test(
        url=args.url,
        concurrency=args.concurrency,
        duration=args.duration,
        warmup=args.warmup
    ))

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info("Đã lưu kết quả load test vào: %s", args.output)


if __name__ == "__main__":
    main()
