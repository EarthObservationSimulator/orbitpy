#include "SliceTree.hpp"

Slice::Slice(Real bound1, Real bound2, const std::vector<Edge> &edges, const std::vector<int> &indices, int level)
{
	this->bound1 = bound1;
	this->bound2 = bound2;
	this->mid = (bound1 + bound2) / 2;
	this->level = level;
	this->saturated = false;

	this->left = this->right = NULL;

	contains(edges,indices);
}

Slice::Slice(Real bound1, Real bound2, const std::vector<Edge> &edges, int level)
{
	this->bound1 = bound1;
	this->bound2 = bound2;
	this->mid = (bound1 + bound2) / 2;
	this->level = level;
	this->saturated = false;

	this->left = this->right = NULL;

	contains(edges);
}

void Slice::contains(const std::vector<Edge> &edges)
{
	for (int i = 0; i < edges.size(); i++)
	{
		this->contained.push_back(i);
	}
}

void Slice::contains(const std::vector<Edge> &edges, const std::vector<int> &indices)
{
	this->saturated = true;
	for (int index : indices)
	{
		Edge edge = edges[index];
		if (contains(edge))
			this->contained.push_back(index);
	}
}

bool Slice::contains(Edge edge)
{
	Real vertex1 = edge.getBound1();
	Real vertex2 = edge.getBound2();

	bool condition1_1 = (vertex1 >= bound1) && (vertex1 <= bound2);
	bool condition1_2 = (vertex2 >= bound1) && (vertex2 <= bound2);

	bool condition2_1 = (bound1 >= vertex1) && (bound1 <= vertex2);
	bool condition2_2 = (bound2 >= vertex1) && (bound2 <= vertex2);

	if (!(condition2_1 && condition2_2))
		this->saturated = false;

	return condition1_1 || condition1_2 || condition2_1 || condition2_2;
}

bool Slice::isSaturated()
{
	return saturated;
}

void Slice::setLeft(Slice* left)
{
	this->left = left;
}

void Slice::setRight(Slice* right)
{
	this->right = right;
}

Slice* Slice::getLeft()
{
	return this->left;
}

Slice* Slice::getRight()
{
	return this->right;
}

int Slice::getLevel()
{
	return this->level;
}

std::vector<int> Slice::getContained()
{
	return contained;
}

Real Slice::getBound1()
{
	return bound1;
}

Real Slice::getBound2()
{
	return bound2;
}

SliceTree::SliceTree(const std::vector<Edge> &edges, Real crit1, Real crit2)
{
	this->crit1 = crit1;
	this->crit2 = crit2;
	this->edges = edges;
	this->height = 0;
}

void SliceTree::preprocess()
{
	Real rootLevel = 0;
	Real theta1 = 0.0;
	Real theta2 = 2 * M_PI;
	root = new Slice(theta1,theta2,edges,rootLevel);

	grow(root);
}

SliceTree::~SliceTree()
{
	deleteTree(this->root);
}

void SliceTree::deleteTree(Slice* node)
{
	if (node == NULL) return;  
  
    deleteTree(node->getLeft());  
    deleteTree(node->getRight());  
      
	delete node; 
}

std::vector<int> SliceTree::getEdges(AnglePair query)
{
	Real theta1, theta2, theta3, lon;
	Slice *temp,*last;

	lon = query[1];

	temp = this->root;
	last = temp;
	while (temp != NULL)
	{
		theta1 = temp->getBound1();
		theta2 = temp->getBound2();
		theta3 = (theta1 + theta2) / 2;

		last = temp;
		if (lon <= theta3)
			temp = temp->getLeft();
		else
			temp = temp->getRight();
	}

	return last->getContained();
}

void SliceTree::grow(Slice* parent)
{

	//return NULL;

	std::vector<int> parentIndices = parent->getContained();
	int parentLevel = parent->getLevel();

	if (parentIndices.size() <= crit1)
		return;
	else if (parent->getLevel() >= crit2)
		return;
	else if (parent->isSaturated())
		return;

	Real theta1 = parent->getBound1();
	Real theta2 = parent->getBound2();
	Real theta3 = (theta1 + theta2) / 2;
	int level = parentLevel + 1;

	Slice* leftChild = new Slice(theta1,theta3,edges,parentIndices,level);
	Slice* rightChild = new Slice(theta3,theta2,edges,parentIndices,level);

	if (parentLevel > this->height)
		this->height = level;

	parent->setLeft(leftChild);
	parent->setRight(rightChild);
	grow(leftChild);
	grow(rightChild);
}