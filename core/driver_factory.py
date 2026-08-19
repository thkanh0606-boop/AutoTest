# core/driver_factory.py

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import (
    SessionNotCreatedException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from core.helpers.utils import get_logger

logger = get_logger()


class DriverFactory:
    """
    Factory tạo Selenium Chrome Driver.

    Mục tiêu:
    - Tránh lỗi Chrome failed to start
    - Tránh lỗi DevToolsActivePort
    - Không dùng chung Chrome profile đang mở
    - Hỗ trợ ChromeDriver qua Selenium Manager
    - Log rõ version Chrome/ChromeDriver để chẩn đoán lỗi session/crash
    - Tương thích với code cũ:
          DriverFactory.create_driver(
              headless=False,
              keep_session=True
          )
    """

    _profile_dirs: set[str] = set()

    # =========================================================
    # CHROME PATH
    # =========================================================

    @staticmethod
    def _find_chrome_binary() -> str | None:
        """
        Tìm Chrome trên Windows.
        """

        candidates = [
            os.environ.get("CHROME_BINARY"),

            r"C:\Program Files\Google\Chrome\Application\chrome.exe",

            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",

            os.path.expandvars(
                r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
            ),
        ]

        for path in candidates:
            if not path:
                continue

            try:
                if os.path.isfile(path):
                    return path
            except Exception:
                continue

        return None

    # =========================================================
    # CHROMEDRIVER PATH
    # =========================================================

    @staticmethod
    def _find_configured_driver() -> str | None:
        """
        Chỉ lấy ChromeDriver được cấu hình bằng environment.

        Không tự động tìm chromedriver.exe lung tung trong project,
        vì rất dễ lấy nhầm ChromeDriver cũ (nguyên nhân phổ biến của
        lỗi "session not created" / crash không rõ message).
        """

        candidates = [
            os.environ.get("CHROMEDRIVER_PATH"),
            os.environ.get("CHROME_DRIVER"),
        ]

        for path in candidates:
            if not path:
                continue

            try:
                if os.path.isfile(path):
                    return path
            except Exception:
                continue

        return None

    # =========================================================
    # TEMP PROFILE
    # =========================================================

    @classmethod
    def _create_profile(cls) -> str:
        """
        Tạo profile Chrome riêng cho Selenium.

        Không dùng profile Chrome người dùng đang mở (đây là nguyên
        nhân phổ biến gây "session deleted because of page crash"
        khi Chrome thật cũng đang mở cùng profile).
        """

        root = (
            Path(tempfile.gettempdir())
            / "autotest_chrome_profiles"
        )

        root.mkdir(
            parents=True,
            exist_ok=True,
        )

        profile_dir = tempfile.mkdtemp(
            prefix="selenium_",
            dir=str(root),
        )

        cls._profile_dirs.add(profile_dir)

        return profile_dir

    # =========================================================
    # OPTIONS
    # =========================================================

    @classmethod
    def _build_options(
        cls,
        headless: bool = False,
        profile_dir: str | None = None,
    ) -> Options:

        options = Options()

        # -----------------------------------------------------
        # Chrome executable
        # -----------------------------------------------------

        chrome_binary = cls._find_chrome_binary()

        if chrome_binary:
            options.binary_location = chrome_binary

        # -----------------------------------------------------
        # Profile riêng
        # -----------------------------------------------------

        if profile_dir:
            options.add_argument(
                f"--user-data-dir={profile_dir}"
            )

        # -----------------------------------------------------
        # Page load strategy
        # -----------------------------------------------------
        # "normal" = chờ document đầy đủ, tránh việc find_element
        # chạy khi trang React/Ant Design chưa kịp hydrate.

        options.page_load_strategy = "normal"

        # -----------------------------------------------------
        # Chrome stability
        # -----------------------------------------------------

        options.add_argument(
            "--no-sandbox"
        )

        options.add_argument(
            "--disable-dev-shm-usage"
        )

        options.add_argument(
            "--disable-gpu"
        )

        options.add_argument(
            "--disable-software-rasterizer"
        )

        options.add_argument(
            "--disable-extensions"
        )

        options.add_argument(
            "--disable-background-networking"
        )

        options.add_argument(
            "--disable-background-timer-throttling"
        )

        options.add_argument(
            "--disable-backgrounding-occluded-windows"
        )

        options.add_argument(
            "--disable-renderer-backgrounding"
        )

        options.add_argument(
            "--disable-popup-blocking"
        )

        options.add_argument(
            "--disable-notifications"
        )

        options.add_argument(
            "--remote-allow-origins=*"
        )

        options.add_argument(
            "--window-size=1440,900"
        )

        # -----------------------------------------------------
        # Disable first run
        # -----------------------------------------------------

        options.add_argument(
            "--no-first-run"
        )

        options.add_argument(
            "--no-default-browser-check"
        )

        options.add_argument(
            "--disable-default-apps"
        )

        # -----------------------------------------------------
        # Headless
        # -----------------------------------------------------

        if headless:
            options.add_argument(
                "--headless=new"
            )

        # -----------------------------------------------------
        # Selenium automation
        # -----------------------------------------------------

        options.add_experimental_option(
            "excludeSwitches",
            [
                "enable-automation",
                "enable-logging",
            ],
        )

        options.add_experimental_option(
            "useAutomationExtension",
            False,
        )

        # -----------------------------------------------------
        # Chrome preferences
        # -----------------------------------------------------

        options.add_experimental_option(
            "prefs",
            {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,

                "profile.default_content_setting_values.notifications": 2,

                "download.prompt_for_download": False,

                "download.directory_upgrade": True,

                "safebrowsing.enabled": True,
            },
        )

        return options

    # =========================================================
    # CREATE WITH SELENIUM MANAGER
    # =========================================================

    @staticmethod
    def _create_with_selenium_manager(
        options: Options,
    ):
        """
        Selenium 4 tự quản lý ChromeDriver (tải bản khớp với Chrome
        đang cài). Đây là cách ưu tiên để tránh dùng ChromeDriver cũ
        không tương thích — nguyên nhân phổ biến nhất của crash
        "chromedriver!GetHandleVerifier..." không có message rõ ràng.
        """

        return webdriver.Chrome(
            options=options
        )

    # =========================================================
    # CREATE WITH MANUAL DRIVER
    # =========================================================

    @staticmethod
    def _create_with_manual_driver(
        options: Options,
        driver_path: str,
    ):
        service = Service(
            executable_path=driver_path
        )

        return webdriver.Chrome(
            service=service,
            options=options,
        )

    # =========================================================
    # VERSION DIAGNOSTICS
    # =========================================================

    @staticmethod
    def describe_driver(driver) -> str:
        """
        Trả về chuỗi mô tả version Chrome / ChromeDriver hiện tại của
        driver, dùng để log khi tạo driver thành công hoặc khi cần
        chẩn đoán crash không rõ nguyên nhân.
        """

        try:
            caps = driver.capabilities or {}

            browser_name = caps.get("browserName", "unknown")
            browser_version = caps.get("browserVersion", "unknown")

            chrome_info = caps.get("chrome", {}) or {}
            chromedriver_version = chrome_info.get(
                "chromedriverVersion", "unknown"
            )

            return (
                f"browser={browser_name} "
                f"browser_version={browser_version} "
                f"chromedriver_version={chromedriver_version} "
                f"session_id={getattr(driver, 'session_id', 'unknown')}"
            )

        except Exception as error:
            return f"(không lấy được version: {error})"

    # =========================================================
    # CREATE DRIVER
    # =========================================================

    @classmethod
    def create_driver(
        cls,
        headless: bool = False,
        keep_session: bool = False,
    ):
        """
        Tạo Chrome Driver.

        keep_session vẫn được giữ để tương thích với project hiện tại.

        Lưu ý:
        Mỗi lần create_driver sẽ có profile riêng.
        Điều này giúp tránh Chrome profile bị khóa.
        """

        profile_dir = cls._create_profile()

        options = cls._build_options(
            headless=headless,
            profile_dir=profile_dir,
        )

        driver = None

        # =====================================================
        # QUAN TRỌNG
        # =====================================================
        #
        # Ưu tiên Selenium Manager.
        #
        # Không dùng chromedriver.exe cũ trong project.
        #
        # Nếu project có:
        #
        # CHROMEDRIVER_PATH
        #
        # thì mới dùng manual driver.
        #
        # =====================================================

        manual_driver = cls._find_configured_driver()

        # -----------------------------------------------------
        # 1. Selenium Manager trước
        # -----------------------------------------------------

        try:

            driver = cls._create_with_selenium_manager(
                options
            )

        except SessionNotCreatedException as session_error:

            # Thường do Chrome đã cài KHÔNG khớp với ChromeDriver mà
            # Selenium Manager tải về (hoặc Chrome quá cũ/mới).
            cls._cleanup_profile(profile_dir)

            raise RuntimeError(
                "Không thể tạo session Chrome (SessionNotCreatedException).\n"
                "Nguyên nhân phổ biến nhất: phiên bản Chrome đang cài "
                "KHÔNG tương thích với ChromeDriver.\n\n"
                f"Chi tiết: {session_error}\n\n"
                "Cách khắc phục:\n"
                "1. Cập nhật Google Chrome lên bản mới nhất.\n"
                "2. Xoá cache Selenium Manager: "
                r"%USERPROFILE%\.cache\selenium"
                " rồi chạy lại.\n"
                "3. Hoặc set biến môi trường CHROMEDRIVER_PATH trỏ tới "
                "chromedriver.exe khớp version Chrome."
            ) from session_error

        except Exception as selenium_manager_error:

            # -------------------------------------------------
            # 2. Nếu Selenium Manager thất bại,
            #    thử driver được cấu hình
            # -------------------------------------------------

            if manual_driver:

                try:

                    driver = cls._create_with_manual_driver(
                        options,
                        manual_driver,
                    )

                except Exception as manual_error:

                    cls._cleanup_profile(
                        profile_dir
                    )

                    raise RuntimeError(
                        "Không thể khởi động Chrome.\n\n"
                        "Selenium Manager:\n"
                        f"{selenium_manager_error}\n\n"
                        "Configured ChromeDriver:\n"
                        f"{manual_error}\n\n"
                        f"ChromeDriver: {manual_driver}"
                    ) from manual_error

            else:

                cls._cleanup_profile(
                    profile_dir
                )

                raise RuntimeError(
                    "Không thể khởi động Chrome bằng "
                    "Selenium Manager.\n\n"
                    f"{selenium_manager_error}\n\n"
                    "Không có CHROMEDRIVER_PATH được cấu hình."
                ) from selenium_manager_error

        # =====================================================
        # DRIVER SETTINGS
        # =====================================================

        try:
            driver.set_page_load_timeout(60)
        except Exception:
            pass

        try:
            driver.set_script_timeout(30)
        except Exception:
            pass

        try:
            driver.implicitly_wait(0)
        except Exception:
            pass

        # =====================================================
        # Save profile path for cleanup
        # =====================================================

        try:
            driver._autotest_profile_dir = profile_dir
        except Exception:
            pass

        # =====================================================
        # LOG VERSION DIAGNOSTICS
        # =====================================================

        try:
            logger.info(
                "[DRIVER] Chrome session created OK. %s",
                cls.describe_driver(driver),
            )
        except Exception:
            pass

        return driver

    # =========================================================
    # SESSION HEALTH CHECK
    # =========================================================

    @staticmethod
    def is_session_alive(driver) -> bool:
        """
        Kiểm tra nhanh session driver còn sống hay không (không crash,
        không bị đóng). Dùng trước các thao tác quan trọng nếu cần.
        """

        if driver is None:
            return False

        try:
            _ = driver.current_url
            return True
        except WebDriverException:
            return False
        except Exception:
            return False

    # =========================================================
    # CLEANUP PROFILE
    # =========================================================

    @classmethod
    def _cleanup_profile(
        cls,
        profile_dir: str | None,
    ):
        if not profile_dir:
            return

        cls._profile_dirs.discard(
            profile_dir
        )

        try:

            if os.path.exists(profile_dir):

                shutil.rmtree(
                    profile_dir,
                    ignore_errors=True,
                )

        except Exception:
            pass

    # =========================================================
    # QUIT DRIVER
    # =========================================================

    @classmethod
    def quit_driver(
        cls,
        driver,
    ):
        """
        Đóng driver và dọn profile tạm.
        """

        if driver is None:
            return

        profile_dir = getattr(
            driver,
            "_autotest_profile_dir",
            None,
        )

        try:
            driver.quit()
        except Exception:
            pass

        # Windows đôi khi cần một khoảng rất nhỏ
        # để Chrome release profile.
        import time

        time.sleep(0.3)

        cls._cleanup_profile(
            profile_dir
        )

    # =========================================================
    # CLEAN ALL
    # =========================================================

    @classmethod
    def cleanup_all_profiles(cls):
        """
        Xóa toàn bộ profile Selenium tạm.
        """

        for profile in list(
            cls._profile_dirs
        ):
            cls._cleanup_profile(
                profile
            )

        root = (
            Path(tempfile.gettempdir())
            / "autotest_chrome_profiles"
        )

        try:

            if root.exists():

                shutil.rmtree(
                    root,
                    ignore_errors=True,
                )

        except Exception:
            pass