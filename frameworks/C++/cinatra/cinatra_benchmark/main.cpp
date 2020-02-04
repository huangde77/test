#include <iostream>
#include <include/cinatra.hpp>

using namespace cinatra;

int main() {
	http_server server(std::thread::hardware_concurrency());
	bool r = server.listen("0.0.0.0", "8090");
	if (!r) {
		std::cout << "listen failed\n";
		return -1;
	}

	server.set_http_handler<GET>("/plaintext", [](request& req, response& res) {
		res.set_status_and_content(status_type::ok, "Hello, World!", res_content_type::string);
	});

	server.run();
	return 0;
}
