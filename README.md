# 🧪 Automated Regression Testing Framework

This project is a **headless browser-based visual regression testing** framework built using **Python**, **Selenium**, and **OpenCV**. It captures screenshots of test scenarios, compares them with baseline reference images, and generates a detailed HTML report with logs and image diffs.

---

## 📁 Project Structure

```
project/
│
├── regression_test.py         # Main testing script
├── init.py                    # Browser setup and helper methods
├── Results/                   # Test result outputs
│   └── [PROD|TEST|ACC]/       # Environment-specific result folders
│       └── Reference/         # Reference images for comparison
```

---

## 🚀 Features

* ✅ **Automated Chrome testing** using `undetected-chromedriver` (headless mode)
* 🖼️ **Screenshot-based comparison** using `SSIM` (Structural Similarity Index)
* 📊 **HTML Report Generation**:

  * Image comparison results
  * Load times
  * Browser console logs
  * Filtering by test status
* 🧪 **Modular test case functions** (easily expandable)
* 🧠 **Automatic environment detection** from URL
* 🧹 **Cleans and organizes logs and screenshots**

---

## 🛠️ Requirements

* Python 3.8+
* Chrome (v138 compatible with `undetected_chromedriver`)
* The following Python libraries:

```bash
pip install selenium undetected-chromedriver opencv-python scikit-image pillow
```

---

## 🔧 Configuration

Modify the login section inside `init.py`:

```python
# init.py
WebDriverWait(self.browser, 20).until(
    EC.presence_of_element_located((By.ID, "YOUR ELEMENT ID"))
).send_keys('YOUR USERNAME')
...
```

Update the element selectors and credentials to match your application under test.

---

## 🧪 Writing Tests

Test functions follow a common pattern:

1. Navigate and interact with UI elements
2. Take a screenshot
3. Store and compare with a reference
4. Log any browser console errors

Example test functions:

```python
def your_test_function1(self): ...
def your_test_function2(self): ...
```

---

## 🖼️ Image Comparison

Uses **SSIM** to compare screenshots:

* If similarity is above threshold (`tolerance=0.999`), the test passes
* If not, a **diff image** is generated and included in the HTML report

You can crop regions of interest using `top_left` and `bottom_right` coordinates.

---

## 📄 HTML Report

The report includes:

* Total test summary (pass/fail)
* Execution duration
* Page load times
* Console logs
* Side-by-side image comparisons
* Dynamic filtering

Example:

```bash
Results/
└── TEST/
    └── 20250722_154501/
        ├── your_test_function1.png
        ├── your_test_function2.png
        ├── diff_your_test_function1.png
        ├── report_20250722_154501.html
```

---

## ✅ Running the Tests

Modify the `url` variable in `regression_test.py` to match your environment.

```python
if __name__ == "__main__":
    url = "https://your.testing.environment/"
```

Then run the script:

```bash
python regression_test.py
```

---

## 📌 Notes

* Screenshots are saved in `Results/<ENV>/<timestamp>/`
* Reference images must exist in `Results/<ENV>/Reference/`
* The environment (`PROD`, `TEST`, `ACC`) is inferred from the URL
* Compatible with Windows-based paths and setups

---

## 🧼 Troubleshooting

* ❌ **Images Not Found?** → Make sure the reference images are placed correctly.
* 🖼 **Images Not Aligned?** → Adjust cropping coordinates in test comparison.
* 🔐 **Login Fails?** → Check element IDs and credentials in `init.py`.
* 🧪 **SSIM < Tolerance?** → Try loosening the `tolerance` if needed.

---

## 🧩 Extend the Framework

Add new test cases by:

1. Creating a function like `your_test_function3()`
2. Adding screenshot calls (`save_ss`)
3. Append to the `comparisons` list
4. Define a matching reference image

---

## 📬 Contact

For questions or contributions, feel free to open an issue or submit a pull request.
