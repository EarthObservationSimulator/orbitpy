#include "SlicedPolygon.hpp"
#include "SliceTree.hpp"
#include <gtest/gtest.h>

class Poly_02 : public ::testing::Test {

	protected:

	void SetUp() override 
	{
		int numElements = 17;
		std::vector<AnglePair> polygon(numElements);
		AnglePair contained = {0,0};
		
        // Initialize cone angles
		polygon[0][0] = 1.047197551;
        polygon[1][0] = 0.7853981634;
        polygon[2][0] = 1.047197551;
        polygon[3][0] = 0.7853981634;
        polygon[4][0] = 1.047197551;
        polygon[5][0] = 0.7853981634;
        polygon[6][0] = 1.047197551;
        polygon[7][0] = 0.7853981634;
        polygon[8][0] = 1.047197551;
        polygon[9][0] = 0.7853981634;
        polygon[10][0] = 1.047197551;
        polygon[11][0] = 0.7853981634;
        polygon[12][0] = 1.047197551;
        polygon[13][0] = 0.7853981634;
        polygon[14][0] = 1.047197551;
        polygon[15][0] = 0.7853981634;
        polygon[16][0] = 1.047197551;

        // Initialize clock angles
        polygon[0][1] = 0.0;
        polygon[1][1] = 0.3926990817;
        polygon[2][1] = 0.7853981634;
        polygon[3][1] = 1.178097245;
        polygon[4][1] = 1.570796327;
        polygon[5][1] = 1.963495408;
        polygon[6][1] = 2.35619449;
        polygon[7][1] = 2.748893572;
        polygon[8][1] = 3.141592654;
        polygon[9][1] = 3.534291735;
        polygon[10][1] = 3.926990817;
        polygon[11][1] = 4.319689899;
        polygon[12][1] = 4.71238898;
        polygon[13][1] = 5.105088062;
        polygon[14][1] = 5.497787144;
        polygon[15][1] = 5.890486225;
        polygon[16][1] = 0.0;
		
        grapefruit = new SlicedPolygon(polygon,contained);
		sliceTree = new SliceTree(grapefruit->getEdgeArray(),1,16);
        sliceTree->preprocess();
        grapefruit->addPreprocessor(sliceTree);
	}

  	void TearDown() override 
  	{
  		delete(grapefruit);
  	}

	Real tol = .00000001;
	SlicedPolygon* grapefruit;
    Preprocessor* sliceTree;
};

TEST_F(Poly_02,Query_01_numCrossings)
{
    // Test 1: Lies inside at same clock angle as one of the polygon points (starting point).
	int expectedCrossings = 0;
	AnglePair query = {0.7853981634,0.0};
	int crossings = grapefruit->numCrossings(query);
	ASSERT_EQ(expectedCrossings,crossings);
}

TEST_F(Poly_02,Query_02_numCrossings)
{
    // Test 2: Lies outside at same clock angle as one of the polygon points (starting point).
	int expectedCrossings = 1;
	AnglePair query = {1.256637061,0.0};
	int crossings = grapefruit->numCrossings(query);
	ASSERT_EQ(expectedCrossings,crossings);
}

TEST_F(Poly_02,Query_03_numCrossings)
{
    // Test 3: Inside, Lies along z-axis 
	int expectedCrossings = 0;
	AnglePair query = {0.0,0.0};
	int crossings = grapefruit->numCrossings(query);
	ASSERT_EQ(expectedCrossings,crossings);
}

TEST_F(Poly_02,Query_05_numCrossings)
{
    // Test 5: Inside, lies along the middle (clock angle) of a segment.
	int expectedCrossings = 0;
	AnglePair query = {0.5235987756,0.1963495408};
	int crossings = grapefruit->numCrossings(query);
	ASSERT_EQ(expectedCrossings,crossings);
}

TEST_F(Poly_02,Query_06_numCrossings)
{
    // Test 5: Outside, lies along the middle (clock angle) of a segment.
	int expectedCrossings = 1;
	AnglePair query = {1.256637061,0.1963495408};
	int crossings = grapefruit->numCrossings(query);
	ASSERT_EQ(expectedCrossings,crossings);
}

int main(int argc, char **argv)
{
	testing::InitGoogleTest(&argc,argv);
	return RUN_ALL_TESTS();
}
