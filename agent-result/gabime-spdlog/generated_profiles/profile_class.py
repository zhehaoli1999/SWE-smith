# Auto-generated profile for gabime/spdlog (cpp)
# Commit: cdbd64e2305a712ec9a360e5a1e05aa1dcab85e7
# Generated: 2025-11-14T14:32:52.488401
# Integration: Copy to swesmith/profiles/cpp.py

@dataclass
class Spdlogcdbd64e2(CppProfile):
    owner: str = "gabime"
    repo: str = "spdlog"
    commit: str = "cdbd64e2305a712ec9a360e5a1e05aa1dcab85e7"
    test_cmd: str = "ctest --output-on-failure --verbose"

    @property
    def dockerfile(self):
        return f"""FROM gcc:latest
RUN apt-get update && apt-get install -y git
RUN git clone https://github.com/{self.mirror_name} /testbed
WORKDIR /testbed
"""

    def log_parser(self, log: str) -> dict[str, str]:
        # Generic parser - customize based on your test framework
        test_status_map = {}
        for line in log.split("\n"):
            if "PASS" in line:
                test_status_map[line.strip()] = "PASSED"
            elif "FAIL" in line:
                test_status_map[line.strip()] = "FAILED"
        return test_status_map


