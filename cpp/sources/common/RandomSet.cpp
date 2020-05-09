#include "RandomSet.h"

#include <random>
#include <ctime>
#include <set>
typedef std::set<size_t> S_SIZE_T;

void RandomSet(V_SIZE_T &pool, size_t elementalSize, V_SIZE_T &subset)
{
	// use current time as random seed
	static std::default_random_engine generator((unsigned)time(0));
	std::uniform_int_distribution<size_t> distribution(0, pool.size() - 1);

	S_SIZE_T randomSet;
	while (randomSet.size() < elementalSize)
		randomSet.insert(distribution(generator));

	for (auto i = randomSet.begin(); i != randomSet.end(); ++i) {
		subset.push_back(pool[*i]);
	}
	return;
}