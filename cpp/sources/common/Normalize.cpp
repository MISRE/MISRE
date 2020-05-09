#include "Normalize.h"

using Eigen::VectorXd;

void Normalize(MatrixXd &point, MatrixXd &H)
{
	H.setIdentity();

	double range = 0;
	for (auto i = 0; i < point.rows() - 1; i++) {
		double range_i = (point.row(i).maxCoeff() - point.row(i).minCoeff()) / 2.;
		if (range_i > range)
			range = range_i;
	}

	for (auto i = 0; i < point.rows() - 1; i++) {
		double mean = point.row(i).sum() / point.cols();
		if (range > 0) {
			H(i, i) = 1. / range;
			H(i, H.cols() - 1) = -mean / range;
		}
	}

	point = H * point;
	return;
}