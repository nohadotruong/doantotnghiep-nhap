# GIẢI THÍCH CHI TIẾT QUY TRÌNH TỪNG BƯỚC CỦA CÁC THUẬT TOÁN

Tài liệu này giải thích chi tiết cách hoạt động từng bước của mỗi thuật toán tìm đường đi cho UAV.

---

## 1. A* (A-STAR) - THUẬT TOÁN TÌM KIẾM ĐỒ THỊ

### Khái Niệm Cơ Bản

A* là thuật toán tìm đường đi **tối ưu** (ngắn nhất) trên đồ thị.

**Công thức chính:**
```
f(n) = g(n) + h(n)

Trong đó:
- f(n): Chi phí tổng cộng để đi qua node n
- g(n): Chi phí thực tế từ start đến node n (Khoảng cách đã đi)
- h(n): Ước lượng chi phí từ node n đến goal (Heuristic)
```

### Quy Trình Hoạt Động

#### **Bước 1: Khởi Tạo**
```
- Đặt g(start) = 0
- Tính h(start) = khoảng cách_euclidean(start, goal)
- Tính f(start) = 0 + h(start)
- Thêm start vào priority queue với ưu tiên f(start)
```

#### **Bước 2: Vòng Lặp Chính**
```
Lặp while priority_queue không rỗng:

1. Lấy node có f(n) nhỏ nhất khỏi priority queue
   - Gọi node này là "current"
   
2. Kiểm tra: Nếu current ≈ goal → Tìm được! Return đường đi
   
3. Thêm current vào closed_set (đã khám phá xong)
```

#### **Bước 3: Khám Phá Hàng Xóm**
```
Với mỗi hàng xóm của current:

1. Tính chi phí mới:
   new_g = g(current) + khoảng_cách(current → hàng_xóm)
   
2. Kiểm tra nếu chi phí mới tốt hơn:
   Nếu hàng_xóm không trong g_scores HOẶC new_g < g(hàng_xóm)
   
3. Cập nhật:
   g(hàng_xóm) = new_g
   h(hàng_xóm) = euclidean(hàng_xóm, goal)
   f(hàng_xóm) = new_g + h(hàng_xóm)
   
4. Thêm hàng_xóm vào priority queue
```

### Ví Dụ Minh Họa

```
Map 5x5:
S . . . .
. # # . .
. . . . #
. . . . .
. . . . G

Start=S(0,0), Goal=G(4,4)

VÒNG 1:
- Current = S(0,0)
- Hàng xóm: (1,0), (0,1), (1,1)
- Cho hàng xóm (1,1):
  * g(1,1) = 0 + sqrt(2) ≈ 1.41
  * h(1,1) = euclidean((1,1)→(4,4)) ≈ 4.24
  * f(1,1) = 1.41 + 4.24 ≈ 5.65

VÒNG 2:
- Chọn hàng xóm có f nhỏ nhất (tính toán cho tất cả)
- Tiếp tục khám phá...

CUỐI CÙNG:
- Khi current = (3,3) hoặc gần G
- Tìm được đường đi S → ... → G
```

### Ưu Điểm & Nhược Điểm

**Ưu điểm:**
- ✓ Luôn tìm được đường đi **tối ưu** (ngắn nhất)
- ✓ **Hiệu quả** (không phải khám phá cả bản đồ)
- ✓ Dùng **heuristic** để hướng dẫn tìm kiếm

**Nhược điểm:**
- ✗ Chậm trên **không gian lớn** (phải khám phá nhiều nút)
- ✗ Chỉ hoạt động trên **grid rời rạc** hoặc đồ thị

---

## 2. PSO (PARTICLE SWARM OPTIMIZATION) - TỐI ƯU HÓA BẦY

### Khái Niệm

PSO mô phỏng hành vi tìm kiếm thức ăn của bầy chim.
- Mỗi hạt (particle) = một giải pháp tiềm năng
- Hạt di chuyển cùng nhau và tìm được nơi tốt nhất

### Công Thức Cập Nhật Vận Tốc

```
v_new = w*v_old + c1*r1*(pbest - x) + c2*r2*(gbest - x)

Trong đó:
- v: vận tốc (hướng và tốc độ di chuyển)
- w: hệ số inertia (0.7) - giữ động lực cũ
- c1: hệ số cognitive (2.0) - kéo về pbest
- c2: hệ số social (2.0) - kéo về gbest
- r1, r2: số ngẫu nhiên (0-1) - tạo sự đa dạng
- pbest: vị trí tốt nhất của hạt này từng có
- gbest: vị trí tốt nhất của cả bầy từng có
- x: vị trí hiện tại
```

### Quy Trình Hoạt Động

#### **Bước 1: Khởi Tạo Bầy Hạt**
```
1. Tạo 30 hạt với vị trí ngẫu nhiên
2. Ghi nhận:
   - pbest[i] = vị trí ban đầu hạt i
   - pbest_score[i] = fitness(pbest[i])
3. Tìm gbest = hạt có pbest_score nhỏ nhất
   - gbest_score = pb best_score nhỏ nhất
```

#### **Bước 2: Vòng Lặp (200 lần)**
```
Lặp for iteration = 0 to 199:

1. CẬP NHẬT TỪNG HẠT:
   For i = 0 to num_particles:
   
   a) Tính vận tốc mới:
      - r1, r2 = random(0, 1) 2 chiều
      - cognitive = c1*r1*(pbest[i] - x[i])  # Kéo về best cá nhân
      - social = c2*r2*(gbest - x[i])        # Kéo về best đám
      - v[i] = 0.7*v_old[i] + cognitive + social
   
   b) Giới hạn vận tốc:
      - v[i] = clamp(v[i], -max_v, max_v)
      - Tránh hạt bay chậy/quá nhanh
   
   c) Cập nhật vị trí:
      - x_new[i] = x[i] + v[i]
      - Nếu va chạm → giữ x[i] cũ
   
   d) Đánh giá fitness:
      - score = distance(x[i], goal)
      - Nếu score < pbest_score[i] → cập nhật pbest
      - Nếu score < gbest_score → cập nhật gbest

2. GHI NHẬN XẾP HẠNG TOÀN BAY:
   - iteration_best_scores.append(gbest_score)
   - Hạ áp xuống để phát hiện hội tụ

3. KIỂM TRA HỘI TỤ:
   - Nếu gbest_score < 5 → dừng sớm
```

### Minh Họa Cụ Thể

```
Ban đầu: 30 hạt phân tán ngẫu nhiên
┌─────────────────┐
│* *  *    *   *  │
│  *   *    *     │
│*    *      *  * │  * = hạt
│   *            │  G = goal
│     *      G   │
└─────────────────┘

Sau 50 iteration: Hạt bắt đầu tập trung
┌─────────────────┐
│              G? │  
│   *   *        │  ? = vị trí một số hạt
│  *  * * *      │
│    *   *       │
│     *   *      │
└─────────────────┘

Sau 100 iteration: Hạt hội tụ gần goal
┌─────────────────┐
│              G  │
│            **   │
│           * *   │
│          * * *  │
│         * *     │
└─────────────────┘
```

### Công Thức Đơn Giản Hóa

Nếu nghĩ đơn giản, hạt chịu 3 lực:
1. **Inertia**: Tiếp tục đi hướng cũ (0.7 * vận tốc cũ)
2. **Self-Learning**: Quay lại vị trí tốt nhất của mình (20% tác động)
3. **Social Learning**: Đi theo hạt tốt nhất bầy (20% tác động)

---

## 3. SA (SIMULATED ANNEALING) - MỤC PHỎNG QUÁ TRÌNH LÀM NGUỘI

### Khái Niệm

SA mô phỏng quá trình làm nguội kim loại trong luyện kim.
- Nhiệt độ cao → Chấp nhận giải pháp xấu hơn (thoát local optimum)
- Nhiệt độ thấp → Chỉ chấp nhận giải pháp tốt hơn (tối ưu hóa)

### Công Thức Chấp Nhận

```
Nếu energy_new < energy_old:
    P(chấp nhận) = 1.0  (chấp nhận 100%)

Nếu energy_new > energy_old (xấu hơn):
    P(chấp nhận) = exp(-(energy_new - energy_old) / T)
    
Trong đó:
- T: nhiệt độ hiện tại
- Nếu T cao → exp(...) lớn → P lớn (dễ chấp nhận)
- Nếu T thấp → exp(...) nhỏ → P nhỏ (khó chấp nhận)
```

### Quy Trình Hoạt Động

#### **Bước 1: Khởi Tạo**
```
1. Tạo giải pháp ban đầu x_0 (random)
2. Tính energy_0 = distance(x_0, goal)
3. best_solution = x_0
4. best_energy = energy_0
5. T = 100 (nhiệt độ ban đầu)
```

#### **Bước 2: Vòng Lặp Làm Nguội (500 lần)**
```
Lặp for iteration = 0 to 499:

1. TẠO GIẢI PHÁP MỚI:
   - Thay đổi nhỏ: x_new = x_old + random(-2, 2)
   - Kiểm tra: không va chạm? → giữ, va chạm? → thử lại

2. TÍNH NĂNG LƯỢNG MỚI:
   - energy_new = distance(x_new, goal)

3. QUYẾT ĐỊNH CHẤP NHẬN:
   a) Nếu energy_new < energy_old:
      → Chấp nhận 100% (tốt hơn)
   
   b) Nếu energy_new >= energy_old (xấu hơn):
      → deltaE = energy_new - energy_old
      → P = exp(-deltaE / T)
      → Nếu random() < P → chấp nhận (với xác suất)
      → Else → từ chối, giữ giải pháp cũ

4. GHI NHẬN TỐT NHẤT:
   - Nếu energy_new < best_energy:
      → best_energy = energy_new
      → best_solution = x_new

5. GHI LẠI LỊCH SỬ:
   - temperature_history.append(T)
   - energy_history.append(best_energy)

6. GIẢM NHIỆT ĐỘ:
   - T = T * cooling_rate
   - T = T * 0.95  (giảm 5% mỗi lần)

7. KIỂM TRA HỘI TỤ:
   - Nếu best_energy < 5 → dừng sớm
```

#### **Biến Thiên Xác Suất Chấp Nhận**

```
Iteration:  10   50   100  200  300  400  500
T:         65   15    6    1   0.5  0.1  0.03
-------
Deltaε=10: 86%  51%  19%   4%   1%   0%    0%
Deltaε=50: 97%  92%  72%  22%   4%   0%    0%

→ Đầu: dễ chấp nhận xấu (tìm rộng)
  Cuối: khó chấp nhận xấu (tối ưu chi tiết)
```

---

## 4. GWO (GREY WOLF OPTIMIZER) - TỐI ƯU HÓA BẦY SÓI XÁM

### Khái Niệm

GWO mô phỏng hành vi săn mồi của bầy sói xám.
- 4 cấp bậc: Alpha (lãnh đạo), Beta (phó), Delta (cảnh sát), Omega (phuc)
- Mỗi sói học từ 3 sói tốt nhất

### Công Thức Cập Nhật Vị Trí

```
X(t+1) = (X_alpha + X_beta + X_delta) / 3 - A·|C·X_best - X|

Trong đó:
- X: vị trí hiện tại
- X_alpha, X_beta, X_delta: vị trí 3 sói tốt nhất
- A, C: các vector điều khiển
- A = 2a·r - a, trong đó r = random(0,1), a = 2 - 2*(t/T)
- C = 2·r
```

### Quy Trình Hoạt Động

#### **Bước 1: Khởi Tạo**
```
1. Tạo 30 sói với vị trí ngẫu nhiên
2. Đánh giá fitness (distance → goal)
3. Sắp xếp và tìm 3 sói tốt nhất:
   - Alpha = sói tốt nhất (fitness nhỏ nhất)
   - Beta = sói thứ 2
   - Delta = sói thứ 3
```

#### **Bước 2: Vòng Lặp (200 lần)**
```
Lặp for iteration = 0 to 199:

1. CẬP NHẬT CÁC HỆ SỐ:
   a = 2 - 2*(iteration / 200)
   
   Iteration:  0   50  100  150  200
   a:          2  1.5  1  0.5   0
   → Lúc đầu tìm rộng (a=2), cuối tối ưu (a=0)

2. CẬP NHẬT TỪNG SÓI:
   For i = 0 to num_wolves:
   
   a) Tính các vector điều khiển:
      r1, r2 = random(0, 1)
      A1 = 2*a*r1 - a  (trong [-a, a])
      C1 = 2*r1
      
      tương tự cho A2,C2 (với beta) và A3,C3 (với delta)
   
   b) San từ alpha:
      X1 = X_alpha - A1 * |C1*X_alpha - X|
   
   c) San từ beta:
      X2 = X_beta - A2 * |C2*X_beta - X|
   
   d) San từ delta:
      X3 = X_delta - A3 * |C3*X_delta - X|
   
   e) Vị trí mới (trung bình 3 hướng):
      X_new = (X1 + X2 + X3) / 3
   
   f) Cập nhật vị trí:
      Nếu X_new không va chạm:
         X[i] = X_new

3. GHI NHẬN 3 SÓI TỐT NHẤT MỚI:
   - Sắp xếp lại fitness
   - Cập nhật alpha, beta, delta (nếu có sói tốt hơn)
   - best_scores_history.append(alpha_score)

4. KIỂM TRA HỘI TỤ:
   - Nếu alpha_score < 5 → dừng sớm
```

### Minh Họa Quá Trình

```
Giai đoạn 1 (a=2): Tìm Kiếm Rộng
- Sói tán loạn khắp không gian
- Xác suất cao chấp nhận giải pháp xấu
- Mục tiêu: khám phá, tìm vùng tốt

Giai đoạn 2 (a=1): Hướng Vào Mục Tiêu
- Sói bắt đầu tập trung vào 3 lãnh đạo
- Cân bằng giữa khám phá và khai thác

Giai đoạn 3 (a=0): Tối Ưu Hóa
- Sói hội tụ chặt chẽ quanh alpha
- Tìm chi tiết quanh mục tiêu
```

---

## 5. GA (GENETIC ALGORITHM) - THUẬT TOÁN DI TRUYỀN

### Khái Niệm

GA mô phỏng quá trình tiến hóa tự nhiên.
- Quần thể gồm các cá thể (individual) = giải pháp
- Qua các thế hệ: **Selection** (chọn) → **Crossover** (lai) → **Mutation** (đột biến)

### Quy Trình Tiến Hóa

#### **Bước 1: Khởi Tạo Quần Thể**
```
1. Tạo 30 cá thể ngẫu nhiên
2. Đánh giá fitness (distance → goal)
3. best_individual = cá thể có fitness nhỏ nhất
```

#### **Bước 2: Vòng Lặp Tiến Hóa (200 thế hệ)**
```
Lặp for generation = 0 to 199:

1. CHỌN LỌC (SELECT):
   - Tournament Selection (đấu loại trực tiếp)
   - Chọn 3 cá thể ngẫu nhiên → lấy cá thể tốt nhất
   - Lặp lại 2 lần → được parent1, parent2
   → Cá thể mạnh có cơ hội sinh sản cao

2. LẢI GHÉP (CROSSOVER):
   - Chọn ngẫu nhiên: blend crossover hay copy?
     * 80% blend crossover
     * 20% copy 1 trong 2 parent
   
   - Blend Crossover:
     parent1 = [30, 40]
     parent2 = [80, 80]
     alpha = [0.3, 0.7] (ngẫu nhiên)
     child = alpha*parent1 + (1-alpha)*parent2
           = [0.3*30 + 0.7*80, 0.7*40 + 0.3*80]
           = [65, 52]
     → Con nằm giữa 2 cha mẹ

3. ĐỘT BIẾN (MUTATE):
   - 10% xác suất đột biến
   - Thay đổi nhỏ: ±2-10 tôi độ
   - Tính năng:
     * Duy trì đa dạng (tranh all giống nhau)
     * Tám va chạm (không tạo ra giải pháp xấu)

4. ELITISM (Giữ Cốt Lõi):
   - Giữ cá thể tốt nhất từ thế hệ cũ vào mới
   - Đảm bảo: giải pháp càng tốt lên chứ không tệ hơn

5. GHI NHẬN:
   - best_fitness_history.append(best_fitness)
   - Mỗi gen, ghi nhận tiến bộ

6. KIỂM TRA HỘI TỤ:
   - Nếu best_fitness < 5 → dừng sớm
```

### Minh Họa Từng Thế Hệ

```
Thế kỷ 0 (Gen 0): Quần thể ngẫu nhiên
┌─────────────────┐
│* *  *    *   *  │
│  *   *    *     │  = Cá thể
│*    *      *  * │
│   *            │  • = Cả thể tốt
│     *      G   │
└─────────────────┘
Best fitness ≈ 80

Thế kỷ 1-20: Tiến hóa cải tiến
├─ Chọn cá thể tốt
├─ Lai ghép để kế thừa tính chất
├─ Đột biến để thám hiểm
└─ Quần thể cải tiến
Best fitness ≈ 60

Thế kỷ 20-50: Hội tụ dần
├─ Cá thể tập trung quanh giải pháp tốt
├─ Ít đột biến, chủ yếu tinh chỉnh
└─ Best fitness ≈ 30

Thế kỷ 50-100: Tối ưu hóa
├─ Quần thể hội tụ quanh 1 vùng
├─ Chỉ đột biến nhẹ để tinh chỉnh
└─ Best fitness ≈ 10

Thế kỷ 100-200: Tối ưu chi tiết
├─ Tất cả cá thể gần giống nhau
├─ Chỉ khác nhau chi tiết nhỏ
└─ Best fitness < 5 (thành công!)
```

### Ưu Điểm GA

```
Lí Do GA Hiệu Quả:
1. TIẾN HÓA: Thế hệ sau học từ thế hệ trước
2. LẢI GHÉP: Kết hợp điểm mạnh của 2 cá thể
3. ĐỘT BIẾN: Tám hiểm mới và thoát local optimum
4. ELITISM: Không bao giờ tệ hơn
5. ĐẦU RỦI: Quần thể đa dạng giúp tìm global optimum
```

---

## Bảng So Sánh Tóm Tắt

| Tiêu Chí | A* | PSO | SA | GWO | GA |
|----------|----|----|----|----|-----|
| **Tìm tối ưu** | ✓✓✓ | ✗ | ✗ | ✗ | ✗ |
| **Tốc độ** | ✓✓ | ✓✓✓ | ✓ | ✓✓ | ✓ |
| **Không gian lớn** | ✗ | ✓✓✓ | ✓✓ | ✓✓ | ✓✓ |
| **Thoát local opt** | Không | ✓ | ✓✓✓ | ✓✓ | ✓✓ |
| **Dễ hiểu** | ✓✓✓ | ✓ | ✓✓ | ✗ | ✓✓ |
| **Điều chỉnh tham số** | ✗ | Phức tạp | Phức tạp | Phức tạp | Phức tạp |

---

## Khi Nào Dùng Thuật Toán Nào

- **A***: Bản đồ nhỏ (<100x100), cần đường đi tối ưu
- **PSO**: Bản đồ vừa (100-500), cần nhanh, hạt để tìm
- **SA**: Bản đồ lớn, cần thoát local optimum
- **GWO**: Bản đồ vừa-lớn, cân bằng tốc độ-chất lượng
- **GA**: Bản đồ lớn, có thời gian, cần giải pháp nhiều dạng

