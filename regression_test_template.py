from init import *


class MyProject:
    def __init__(self, url):
        if "production" in url:
            self.env_dir = "PROD"
        elif "test" in url:
            self.env_dir = "TEST"
        elif "accept" in url:
            self.env_dir = "ACC"
        elif "localhost" in url:
            self.env_dir = "TEST"
        else:
            raise ValueError("Invalid URL environment")

        self.results_dir = os.path.join("Results", self.env_dir)
        os.makedirs(self.results_dir, exist_ok=True)
        self.test_case_counter = 0
        self.project_name = f"test_project_{str(uuid.uuid4())[:5]}"
        self.reference_dir = os.path.join(
            "C:\\Projects\\ProjectA\\tests\\regression_test\\Results",
            self.env_dir,
            "Reference",
        )

    def setup_logger(self, log_name=None):
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")

        log_dir = self.current_results_dir
        os.makedirs(log_dir, exist_ok=True)

        log_file_name = f"{log_name or 'log'}_{timestamp}.html"
        log_file_path = os.path.join(log_dir, log_file_name)
        self.log_file_path = log_file_path
        logging.basicConfig(
            filename=log_file_path,
            level=logging.INFO,
            format="%(asctime)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def log_browser_console(self, test_name):
        logs = self.browser.get_log("browser")
        error_count = Counter()
        unique_errors = set()
        has_error = False

        excluded_error_messages = [
            "patching driver executable",
            "https://westeurope-5.in.applicationinsights.azure.com/v2/track",
            "401 (Unauthorized)",
            "favicon.ico",
            "clarity",
            "translate(0,NaN)",
            "pcg-brushes"
        ]

        log_entries = []

        for log in logs:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_message = log["message"]
            error_level = log.get("level", "INFO")
            error_key = f"{timestamp} - {error_message}"

            if any(excluded in error_message for excluded in excluded_error_messages):
                continue

            if error_level == "SEVERE" and error_key not in unique_errors:
                has_error = True
                log_entry = (
                    f"<p style='color:red;'>"
                    f"{timestamp} - Browser Error: {error_message}<br>"
                )
                log_entries.append(log_entry)
                error_count[error_message] += 1
                unique_errors.add(error_key)

        if has_error:
            self.setup_logger(test_name)
            with open(self.log_file_path, "w") as log_file:
                log_file.write("<html><body>\n")
                log_file.write(f"<h3>{test_name}</h3>\n")
                for entry in log_entries:
                    log_file.write(entry)
                for error_message, count in error_count.items():
                    if count > 1:
                        log_file.write(
                            f"<p style='color:red;'>Error '{error_message}' occurred {count} times.</p>\n"
                        )
                log_file.write("</body></html>\n")

    def create_new_result_dir(self):
        now = datetime.now()
        self.timestamp = now.strftime("%Y%m%d_%H%M%S")
        self.current_results_dir = os.path.join(self.results_dir, self.timestamp)
        os.makedirs(self.current_results_dir, exist_ok=True)

    def setup_chrome(self, url):
        self.setup = Setup()
        self.browser = self.setup.browser
        mp.actions = self.setup.actions
        self.browser.get(url)
        self.browser.maximize_window()

    def login(self):
        self.setup.login()

    def click_element(self, xpath):
        WebDriverWait(self.browser, 30).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        ).click()
        sleep(1)

    def clear_textbox(self, xpath):
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        ).clear()
        sleep(1)

    def mouse_click_element(self, xpath):
        element = WebDriverWait(self.browser, 30).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )

        actions = ActionChains(self.browser)
        actions.move_to_element(element).click().perform()
        sleep(1)

    def wait_for_element(self, xpath):
        WebDriverWait(self.browser, 60).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        sleep(1)

    def double_click_element(self, xpath):
        element = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        mp.actions.double_click(element).perform()
        sleep(1)

    def send_keys_to_element(self, xpath, keys):
        element = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        element.send_keys(keys)

    def get_value(self, xpath):
        element = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )

        value_str = element.get_attribute("value")

        if not value_str:
            value_str = element.text or element.get_attribute("innerText")

        if not value_str:
            print(f"Value could not be found at {xpath}")
            return None

        try:
            cleaned_value = float(value_str.replace(".", "").replace(",", "."))
            return cleaned_value
        except ValueError:
            print(f"Convert issue: '{value_str}'")
            return None

    def get_cleaned_value(self, xpath, index):
        try:
            element = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )

            value_str = element.get_attribute("value")

            if value_str:
                parts = value_str.split()
                if index < len(parts):
                    part = parts[index]
                    if part.endswith("st"):
                        cleaned_value = part[:-2]
                        try:
                            return int(cleaned_value)
                        except ValueError:
                            print(
                                f"Convert issue: '{cleaned_value}' is not a valid integer."
                            )
                            return 0
                print(
                    f"No valid integer found in value: '{value_str}' at index {index}"
                )
                return 0
            else:
                print(f"No value found for xpath: {xpath}")
                return 0
        except Exception as e:
            print(f"Error occurred: {e}")
            return 0

    def save_ss(self, filename):
        self.browser.save_screenshot(os.path.join(self.current_results_dir, filename))

    def load_page(self, xpath, feature, load_times):
        start_time = time.time()

        self.wait_for_element(xpath)

        load_time = time.time() - start_time
        print(f"\n\n\n{feature} Page has been loaded within {load_time:.2f} seconds.")
        load_times[feature] = load_time
        sleep(1)

    def load_page_and_double_click(self, xpath, feature, load_times):
        start_time = time.time()

        self.wait_for_element(xpath)
        self.double_click_element(xpath)

        load_time = time.time() - start_time
        print(f"\n\n\n{feature} Page has been loaded within {load_time:.2f} seconds.")
        load_times[feature] = load_time
        sleep(1)

    def close_popup(self):
        mp.click_element('//*[@id="dialog-paper"]')
        for _ in range(2):
            mp.actions.send_keys(Keys.TAB).perform()
        sleep(1)
        mp.actions.send_keys(Keys.RETURN).perform()
        sleep(1)

    def change_sm_value(self, xpath):
        for _ in range(2):
            mp.double_click_element(xpath)
            mp.click_element(xpath)
            mp.click_element("//*[contains(text(), 'Boven')]")
            mp.actions.send_keys(Keys.ESCAPE).perform()
            sleep(1)

    def your_test_function1(self):
        for _ in range(6):
            mp.click_element('//*[@id="map"]/div[3]/div[5]/div[1]/button[1]')

        mp.click_element(
            '//*[@id="root"]/div/div/div/div[2]/div[2]/div[1]/div/div/div/div[2]/div/div[2]/div[1]/div/div[2]/div[2]/div/button'
        )
        sleep(5)

        mp.send_keys_to_element('//*[@id="max-build-size"]', "60")
        sleep(1)

        for _ in range(3):
            mp.actions.send_keys(Keys.TAB).perform()
        mp.actions.send_keys(Keys.DOWN).perform()
        sleep(1)
        mp.actions.send_keys(Keys.RETURN).perform()
        sleep(1)
        mp.actions.send_keys(Keys.TAB).perform()
        for _ in range(2):
            mp.actions.send_keys(Keys.DOWN).perform()
        sleep(1)
        mp.actions.send_keys(Keys.RETURN).perform()
        sleep(1)
        mp.actions.send_keys(Keys.TAB).perform()
        mp.actions.send_keys(Keys.SPACE).perform()
        sleep(1)

        mp.click_element("//*[contains(text(), 'Meet')]")
        sleep(3)

        mp.save_ss("your_test_function1.png")
        mp.log_browser_console("Your Test Function 1")

    def your_test_function2(self):
        mp.click_element("//*[contains(text(), 'Voorselectie')]")
        mp.click_element('//*[@id="type-power-rack-select"]')

        mp.actions.send_keys(Keys.ESCAPE).perform()
        sleep(1)

        mp.click_element('//*[@id="type-cooling-principle-select"]')
        mp.actions.send_keys(Keys.RETURN).perform()
        mp.actions.send_keys(Keys.ESCAPE).perform()
        sleep(1)

        mp.save_ss("whitespace_default.png")
        mp.click_element("//*[contains(text(), 'Selecteer alles')]")
        mp.save_ss("whitespace_select_all.png")
        mp.click_element(
            '//*[@id="full-width-tabpanel-1"]/div/div/div/div[2]/div[2]/div/div[1]/div[3]/button'
        )
        mp.save_ss("whitespace_reset_all.png")

        mp.click_element("(//*[contains(text(), 'Selecteer')])[12]")
        sleep(3)
        mp.save_ss("whitespace_one_item_selected.png")

        mp.double_click_element(
            '//*[@id="full-width-tabpanel-1"]/div/div/div/div[2]/div[1]/div/div/div/div/div/div[1]'
        )
        mp.wait_for_element('//*[@id="axes_1"]')
        mp.save_ss("whitespace_2D.png")
        mp.click_element("//*[contains(text(), '3D')]")
        sleep(2)

        mp.save_ss("your_test_function2.png")
        mp.log_browser_console("Your Test Function 2")

    def close_browser(self):
        self.setup.close_browser()

    def crop_image(self, image_path, top_left, bottom_right):
        with Image.open(image_path) as img:
            cropped_img = img.crop((*top_left, *bottom_right))
        return cropped_img

    def compare_images(
            self,
            image1_path,
            image2_path,
            diff_save_path=None,
            tolerance=0.999,
            top_left=(0, 0),
            bottom_right=None,
    ):
        try:
            if not os.path.exists(image1_path) or not os.path.exists(image2_path):
                raise IOError(
                    f"One or both image files not found: {image1_path}, {image2_path}"
                )

            image1 = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
            image2 = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)

            if image1 is None or image2 is None:
                raise IOError(f"Error loading images: {image1_path} or {image2_path}")

            if bottom_right is not None:
                image1 = image1[
                         top_left[1]: bottom_right[1], top_left[0]: bottom_right[0]
                         ]
                image2 = image2[
                         top_left[1]: bottom_right[1], top_left[0]: bottom_right[0]
                         ]

            if image1.shape != image2.shape:
                print(
                    f"Error: Images {image1_path} and {image2_path} have different dimensions."
                )
                return False

            similarity_score = ssim(image1, image2)

            if similarity_score > tolerance:
                return True
            else:
                if diff_save_path:
                    diff = cv2.absdiff(image1, image2)
                    diff = (255 * (diff / np.max(diff))).astype("uint8")
                    cv2.imwrite(diff_save_path, diff)
                return False

        except IOError as e:
            print(str(e))
            if diff_save_path:
                empty_img = np.zeros((100, 100), dtype=np.uint8)
                cv2.imwrite(diff_save_path, empty_img)
            return False

    def generate_report(self, test_results, start_time, load_times):
        if not isinstance(test_results, list):
            raise TypeError(
                "Expected a list of test results but got: {}".format(type(test_results))
            )

        end_time = datetime.now()
        passed_tests = sum(1 for result in test_results if result["result"])
        failed_tests = len(test_results) - passed_tests
        test_duration = end_time - start_time

        report_filename = f"report_{end_time.strftime('%Y%m%d_%H%M%S')}.html"
        report_path = os.path.join(self.current_results_dir, report_filename)

        html_files = [
            file
            for file in os.listdir(self.current_results_dir)
            if file.endswith(".html")
        ]

        with open(report_path, "w", encoding="utf-8") as report_file:
            report_file.write("<html><head><style>")
            report_file.write(
                """
                body { font-family: Arial, sans-serif; background-color: #f0f0f0; color: #333; }
                h1 { color: #2c3e50; }
                h2 { color: #34495e; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
                th { background-color: #2c3e50; color: white; position: sticky; top: 0; z-index: 1; }
                img { max-width: 300px; height: auto; }
                a { text-decoration: none; color: #2980b9; }
                a:hover { text-decoration: underline; }
                .fail-result { color: #e74c3c; }
                .pass-result { color: #27ae60; }
                .test-row { display: table-row; }
                .hidden { display: none; }
                """
            )
            report_file.write("</style>")

            report_file.write(
                """
                <script>
                    function filterTests() {
                        var filter = document.getElementById("filter").value;
                        var rows = document.getElementsByClassName("test-row");
                        for (var i = 0; i < rows.length; i++) {
                            var resultClass = rows[i].classList.contains("pass") ? "pass" : "fail";
                            rows[i].style.display = (filter === "all" || filter === resultClass) ? "" : "none";
                        }
                    }
                </script>
                """
            )

            report_file.write("</head><body>")

            report_file.write(
                f"<h1>Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h1>"
            )
            report_file.write(
                f"<p><strong>Test Start Time:</strong> {start_time.strftime('%Y-%m-%d %H:%M:%S')}</p>"
            )
            report_file.write(
                f"<p><strong>Test End Time:</strong> {end_time.strftime('%Y-%m-%d %H:%M:%S')}</p>"
            )
            report_file.write(
                f"<p><strong>Total Duration:</strong> {str(test_duration)}</p>"
            )
            report_file.write(
                f"<p><strong>Total Tests:</strong> {len(test_results)}</p>"
            )
            report_file.write(f"<p><strong>Passed Tests:</strong> {passed_tests}</p>")
            report_file.write(f"<p><strong>Failed Tests:</strong> {failed_tests}</p>")

            report_file.write("<h2>Page Load Times</h2>")
            report_file.write(
                "<table><tr><th>Page Name</th><th>Load Time (seconds)</th></tr>"
            )
            for feature, load_time in load_times.items():
                report_file.write(
                    f"<tr><td>{feature} Page</td><td>{load_time:.2f}</td></tr>"
                )
            report_file.write("</table>")

            report_file.write("<h2>Log Files</h2>")
            if html_files:
                report_file.write("<ul>")
                for log_file in html_files:
                    log_path = os.path.abspath(
                        os.path.join(self.current_results_dir, log_file)
                    )
                    report_file.write(
                        f"<li><a href='file://{log_path}' target='_blank'>{log_file}</a></li>"
                    )
                report_file.write("</ul>")
            else:
                report_file.write("<p>No log files found.</p>")

            report_file.write(
                """
                <h2>Test Results</h2>
                <label for="filter">Show: </label>
                <select id="filter" onchange="filterTests()">
                    <option value="all">All</option>
                    <option value="pass">Passed</option>
                    <option value="fail">Failed</option>
                </select>
                """
            )
            report_file.write(
                "<table><tr>"
                "<th>Test Name</th>"
                "<th>Result</th>"
                "<th>Duration (s)</th>"
                "<th>New Image</th>"
                "<th>Reference Image</th>"
                "<th>Diff Image</th>"
                "<th>Calculation Details</th>"
                "</tr>"
            )

            for result in test_results:
                test_name = result["name"]
                test_result = result["result"]
                duration = result.get("duration")
                reference = result.get("reference")
                new = result.get("new")
                diff = result.get("diff")
                result_class = "pass" if test_result else "fail"
                result_class_for_result = "pass-result" if test_result else "fail-result"

                is_image_test = isinstance(reference, str) and reference.lower().endswith((".png", ".jpg", ".jpeg"))

                report_file.write(f"<tr class='test-row {result_class}'>")

                report_file.write(f"<td class='test-name'>{test_name}</td>")
                report_file.write(f"<td class='{result_class_for_result}'>{'Passed' if test_result else 'Failed'}</td>")
                report_file.write(f"<td>{duration:.2f} s</td>" if duration else "<td><em>N/A</em></td>")

                if is_image_test:
                    report_file.write(
                        f"<td><a href='{os.path.abspath(new)}' target='_blank'><img src='{os.path.abspath(new)}' alt='New Image'></a></td>"
                    ) if new else report_file.write("<td><em>Not Available</em></td>")

                    report_file.write(
                        f"<td><a href='{os.path.abspath(reference)}' target='_blank'><img src='{os.path.abspath(reference)}' alt='Reference Image'></a></td>"
                    ) if reference else report_file.write("<td><em>Not Available</em></td>")

                    report_file.write(
                        f"<td><a href='{os.path.abspath(diff)}' target='_blank'><img src='{os.path.abspath(diff)}' alt='Difference Image'></a></td>"
                    ) if diff else report_file.write("<td><em>Not Available</em></td>")

                    report_file.write("<td><em>N/A</em></td>")

                else:
                    report_file.write("<td><em>N/A</em></td>" * 3)

                    report_file.write("<td>")
                    if reference is not None:
                        report_file.write(f"<strong>Expected:</strong> {reference}<br>")
                    else:
                        report_file.write(f"<strong>Expected:</strong> N/A<br>")

                    if new is not None:
                        report_file.write(f"<strong>Actual:</strong> {new}<br>")
                    else:
                        report_file.write(f"<strong>Actual:</strong> N/A<br>")

                    if diff is not None:
                        report_file.write(f"<strong>Difference:</strong> {diff}")
                    report_file.write("</td>")

                report_file.write("</tr>")


if __name__ == "__main__":
    url = "https://www.yourtestenvironmentlink.com/"

    load_times = {}
    mp = MyProject(url)
    start_time = datetime.now()
    mp.create_new_result_dir()

    mp.setup_chrome(url)
    mp.login()


    def run_test(comparisons, mp):
        all_tests_passed = True
        test_results = []

        for comparison in comparisons:
            if not isinstance(comparison, dict):
                raise TypeError("Each comparison entry should be a dictionary.")

            required_keys = ["name", "reference", "new", "diff"]
            for key in required_keys:
                if key not in comparison:
                    raise KeyError(f"Missing required key: {key}")

            test_result = mp.compare_images(
                comparison.get("reference"),
                comparison.get("new"),
                comparison.get("diff"),
                top_left=comparison.get("top_left", (0, 0)),
                bottom_right=comparison.get("bottom_right"),
            )
            test_results.append(
                {
                    "name": comparison.get("name"),
                    "result": test_result,
                    "reference": comparison.get("reference"),
                    "new": comparison.get("new"),
                    "diff": comparison.get("diff") if not test_result else None,
                }
            )

            if test_result:
                print(f"Test Passed: {comparison.get('name')} images are identical.")
            else:
                print(f"Test Failed: {comparison.get('name')} images are different.")
                all_tests_passed = False

        return test_results, all_tests_passed


    def projectA_test(mp):
        comparisons = []
        try:
            try:
                mp.your_test_function1()
            except:
                error_message = traceback.format_exc()
                print(error_message)
                mp.log_browser_console("Your Test Function 1 Error Log")

            try:
                mp.your_test_function2()
            except:
                error_message = traceback.format_exc()
                print(error_message)
                mp.log_browser_console("Your Test Function 2 Error Log")

            comparisons = [
                {
                    "name": "your_test_function1",
                    "reference": os.path.join(
                        mp.reference_dir, "your_test_function1.png"
                    ),
                    "new": os.path.join(
                        mp.current_results_dir, "your_test_function1.png"
                    ),
                    "diff": os.path.join(
                        mp.current_results_dir, "diff_your_test_function1.png"
                    ),
                    "top_left": (8, 10),
                    "bottom_right": (305, 675),
                },
                {
                    "name": "your_test_function2",
                    "reference": os.path.join(
                        mp.reference_dir, "your_test_function2.png"
                    ),
                    "new": os.path.join(
                        mp.current_results_dir, "your_test_function2.png"
                    ),
                    "diff": os.path.join(
                        mp.current_results_dir, "diff_your_test_function2.png"
                    ),
                    "top_left": (8, 10),
                    "bottom_right": (200, 300),
                }
            ]

        except:
            error_message = traceback.format_exc()
            print(error_message)
            mp.log_browser_console("Project-A Error Log")
            sleep(5)
        print("\n\n\nPROJECT-A TEST RESULT\n\n")
        test_results, all_tests_passed = run_test(comparisons, mp)
        return test_results, all_tests_passed


    all_results = []
    all_tests_passed = True

    results, tests_passed = projectA_test(mp)
    all_results.extend(results)
    all_tests_passed &= tests_passed

    mp.generate_report(all_results, start_time, load_times)

    if all_tests_passed:
        print("Test Passed: All images are identical.")
    else:
        print("Test Failed: One or more images are different.")

    mp.close_browser()
